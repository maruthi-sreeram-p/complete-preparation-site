package dev.javatrail.notes.config;

import java.util.LinkedHashMap;
import java.util.Map;

import dev.javatrail.notes.auth.EmailTakenException;
import dev.javatrail.notes.auth.InvalidLoginException;
import dev.javatrail.notes.note.NoteConflictException;
import dev.javatrail.notes.note.NoteNotFoundException;

import org.springframework.dao.OptimisticLockingFailureException;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.HttpStatusCode;
import org.springframework.http.ProblemDetail;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.context.request.WebRequest;
import org.springframework.web.servlet.mvc.method.annotation.ResponseEntityExceptionHandler;

/** One place that turns exceptions into RFC 9457 problem responses the React app can read. */
@RestControllerAdvice
class ApiExceptionHandler extends ResponseEntityExceptionHandler {

    @Override
    protected ResponseEntity<Object> handleMethodArgumentNotValid(MethodArgumentNotValidException ex,
            HttpHeaders headers, HttpStatusCode status, WebRequest request) {
        Map<String, String> errors = new LinkedHashMap<>();
        ex.getBindingResult().getFieldErrors().forEach(f -> errors.putIfAbsent(f.getField(), f.getDefaultMessage()));
        ProblemDetail problem = ProblemDetail.forStatusAndDetail(HttpStatus.BAD_REQUEST, "Some fields are invalid.");
        problem.setTitle("Validation failed");
        problem.setProperty("errors", errors);
        return ResponseEntity.badRequest().body(problem);
    }

    @ExceptionHandler(NoteNotFoundException.class)
    ProblemDetail notFound() {
        ProblemDetail problem = ProblemDetail.forStatusAndDetail(HttpStatus.NOT_FOUND, "That note does not exist.");
        problem.setTitle("Not found");
        return problem;
    }

    @ExceptionHandler({NoteConflictException.class, OptimisticLockingFailureException.class})
    ProblemDetail conflict() {
        ProblemDetail problem = ProblemDetail.forStatusAndDetail(HttpStatus.CONFLICT,
            "Someone else changed this note. Reload it to see the latest version.");
        problem.setTitle("Edit conflict");
        return problem;
    }

    @ExceptionHandler(EmailTakenException.class)
    ProblemDetail emailTaken() {
        ProblemDetail problem = ProblemDetail.forStatusAndDetail(HttpStatus.CONFLICT, "That email is already registered.");
        problem.setTitle("Email taken");
        problem.setProperty("errors", Map.of("email", "That email is already registered"));
        return problem;
    }

    @ExceptionHandler(InvalidLoginException.class)
    ProblemDetail invalidLogin() {
        ProblemDetail problem = ProblemDetail.forStatusAndDetail(HttpStatus.UNAUTHORIZED, "Email or password is wrong.");
        problem.setTitle("Sign-in failed");
        return problem;
    }
}
