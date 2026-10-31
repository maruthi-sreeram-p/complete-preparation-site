package dev.javatrail.notes.note;

import java.time.Instant;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

/** What goes over the wire: the entity itself never leaves the service. */
public final class NoteDtos {

    private NoteDtos() {}

    public record NoteView(long id, String title, String body, long version, Instant updatedAt) {
        static NoteView of(Note n) {
            return new NoteView(n.getId(), n.getTitle(), n.getBody(), n.getVersion(), n.getUpdatedAt());
        }
    }

    /** version is required for an update, and ignored for a create. */
    public record SaveNote(@NotBlank @Size(max = 120) String title,
                           @Size(max = 5000) String body,
                           Long version) {}
}
