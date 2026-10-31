package dev.javatrail.notes.config;

import java.time.Duration;

import org.springframework.boot.context.properties.ConfigurationProperties;

/** Settings under "app." in application.yml. */
@ConfigurationProperties("app")
public record AppProperties(Jwt jwt, Cookie cookie) {

    public record Jwt(String secret, Duration ttl) {
        public Jwt {
            ttl = ttl == null ? Duration.ofHours(8) : ttl;
        }
    }

    public record Cookie(boolean secure) {}
}
