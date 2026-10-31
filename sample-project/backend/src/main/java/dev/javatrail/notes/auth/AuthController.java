package dev.javatrail.notes.auth;

import java.time.Duration;
import java.time.Instant;
import java.util.Locale;

import jakarta.validation.Valid;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

import dev.javatrail.notes.config.AppProperties;
import dev.javatrail.notes.config.SecurityConfig;
import dev.javatrail.notes.user.AppUser;
import dev.javatrail.notes.user.UserRepository;

import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseCookie;
import org.springframework.http.ResponseEntity;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.oauth2.jose.jws.MacAlgorithm;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.security.oauth2.jwt.JwsHeader;
import org.springframework.security.oauth2.jwt.JwtClaimsSet;
import org.springframework.security.oauth2.jwt.JwtEncoder;
import org.springframework.security.oauth2.jwt.JwtEncoderParameters;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api")
class AuthController {

    record RegisterRequest(@NotBlank @Email @Size(max = 255) String email,
                           @NotBlank @Size(min = 8, max = 72) String password) {   // BCrypt reads at most 72 bytes
        RegisterRequest {
            email = email == null ? null : email.trim();   // pasted emails often carry spaces: trim before validating
        }
    }

    record LoginRequest(@NotBlank String email, @NotBlank String password) {
        LoginRequest {
            email = email == null ? null : email.trim();
        }
    }

    record UserView(long id, String email) {}

    private final UserRepository users;
    private final PasswordEncoder encoder;
    private final JwtEncoder jwtEncoder;
    private final AppProperties props;
    private final String dummyHash;

    AuthController(UserRepository users, PasswordEncoder encoder, JwtEncoder jwtEncoder, AppProperties props) {
        this.users = users;
        this.encoder = encoder;
        this.jwtEncoder = jwtEncoder;
        this.props = props;
        // checked when the email is unknown, so that "no such user" takes as long as "wrong password"
        this.dummyHash = encoder.encode("not-a-real-password");
    }

    @PostMapping("/auth/register")
    ResponseEntity<UserView> register(@Valid @RequestBody RegisterRequest request) {
        String email = normalise(request.email());
        if (users.existsByEmail(email)) {
            throw new EmailTakenException();
        }
        AppUser user;
        try {
            user = users.save(new AppUser(email, encoder.encode(request.password())));
        } catch (DataIntegrityViolationException e) {
            throw new EmailTakenException();   // lost a race with another registration of the same email
        }
        return signedIn(HttpStatus.CREATED, user);
    }

    @PostMapping("/auth/login")
    ResponseEntity<UserView> login(@Valid @RequestBody LoginRequest request) {
        AppUser user = users.findByEmail(normalise(request.email())).orElse(null);
        String hash = user != null ? user.getPasswordHash() : dummyHash;
        boolean matches = encoder.matches(request.password(), hash);
        if (user == null || !matches) {
            throw new InvalidLoginException();
        }
        return signedIn(HttpStatus.OK, user);
    }

    @PostMapping("/auth/logout")
    ResponseEntity<Void> logout() {
        return ResponseEntity.noContent().header(HttpHeaders.SET_COOKIE, cookie("", Duration.ZERO).toString()).build();
    }

    @GetMapping("/me")
    UserView me(@AuthenticationPrincipal Jwt jwt) {
        return new UserView(Long.parseLong(jwt.getSubject()), jwt.getClaimAsString("email"));
    }

    private ResponseEntity<UserView> signedIn(HttpStatus status, AppUser user) {
        Instant now = Instant.now();
        JwtClaimsSet claims = JwtClaimsSet.builder()
            .issuer("notes-api")
            .subject(String.valueOf(user.getId()))
            .claim("email", user.getEmail())
            .issuedAt(now)
            .expiresAt(now.plus(props.jwt().ttl()))
            .build();
        String token = jwtEncoder.encode(
            JwtEncoderParameters.from(JwsHeader.with(MacAlgorithm.HS256).build(), claims)).getTokenValue();
        return ResponseEntity.status(status)
            .header(HttpHeaders.SET_COOKIE, cookie(token, props.jwt().ttl()).toString())
            .body(new UserView(user.getId(), user.getEmail()));
    }

    private ResponseCookie cookie(String value, Duration maxAge) {
        return ResponseCookie.from(SecurityConfig.COOKIE_NAME, value)
            .httpOnly(true)                       // scripts cannot read it, so an XSS flaw cannot steal it
            .secure(props.cookie().secure())
            .sameSite("Strict")                   // never sent on cross-site requests
            .path("/")
            .maxAge(maxAge)
            .build();
    }

    private static String normalise(String email) {
        return email.trim().toLowerCase(Locale.ROOT);
    }
}
