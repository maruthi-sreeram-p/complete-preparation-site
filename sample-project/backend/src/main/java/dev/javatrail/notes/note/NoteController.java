package dev.javatrail.notes.note;

import java.net.URI;

import jakarta.validation.Valid;

import dev.javatrail.notes.note.NoteDtos.NoteView;
import dev.javatrail.notes.note.NoteDtos.SaveNote;

import org.springframework.data.web.PagedModel;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/notes")
class NoteController {

    private final NoteService notes;

    NoteController(NoteService notes) {
        this.notes = notes;
    }

    @GetMapping
    PagedModel<NoteView> list(@AuthenticationPrincipal Jwt jwt,
                              @RequestParam(defaultValue = "") String q,
                              @RequestParam(defaultValue = "0") int page,
                              @RequestParam(defaultValue = "20") int size) {
        return new PagedModel<>(notes.list(ownerId(jwt), q, page, size));
    }

    @GetMapping("/{id}")
    NoteView get(@AuthenticationPrincipal Jwt jwt, @PathVariable long id) {
        return notes.get(ownerId(jwt), id);
    }

    @PostMapping
    ResponseEntity<NoteView> create(@AuthenticationPrincipal Jwt jwt, @Valid @RequestBody SaveNote body) {
        NoteView saved = notes.create(ownerId(jwt), body);
        return ResponseEntity.created(URI.create("/api/notes/" + saved.id())).body(saved);
    }

    @PutMapping("/{id}")
    NoteView update(@AuthenticationPrincipal Jwt jwt, @PathVariable long id, @Valid @RequestBody SaveNote body) {
        return notes.update(ownerId(jwt), id, body);
    }

    @DeleteMapping("/{id}")
    ResponseEntity<Void> delete(@AuthenticationPrincipal Jwt jwt, @PathVariable long id) {
        notes.delete(ownerId(jwt), id);
        return ResponseEntity.noContent().build();
    }

    /** The owner always comes from the verified token, never from the request. */
    private static long ownerId(Jwt jwt) {
        return Long.parseLong(jwt.getSubject());
    }
}
