package dev.javatrail.notes.note;

import java.util.Locale;

import dev.javatrail.notes.note.NoteDtos.NoteView;
import dev.javatrail.notes.note.NoteDtos.SaveNote;

import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@Transactional
public class NoteService {

    private static final int MAX_PAGE_SIZE = 100;

    private final NoteRepository notes;

    NoteService(NoteRepository notes) {
        this.notes = notes;
    }

    @Transactional(readOnly = true)
    public Page<NoteView> list(long ownerId, String query, int page, int size) {
        // the sort is fixed on the server: a client-supplied sort could name any property
        PageRequest request = PageRequest.of(Math.max(page, 0), Math.min(Math.max(size, 1), MAX_PAGE_SIZE),
            Sort.by(Sort.Direction.DESC, "updatedAt").and(Sort.by(Sort.Direction.DESC, "id")));
        return notes.search(ownerId, likePattern(query), request).map(NoteView::of);
    }

    @Transactional(readOnly = true)
    public NoteView get(long ownerId, long id) {
        return NoteView.of(owned(ownerId, id));
    }

    public NoteView create(long ownerId, SaveNote body) {
        Note saved = notes.save(new Note(ownerId, body.title().trim(), orEmpty(body.body())));
        return NoteView.of(saved);
    }

    public NoteView update(long ownerId, long id, SaveNote body) {
        Note note = owned(ownerId, id);
        if (body.version() == null || body.version() != note.getVersion()) {
            throw new NoteConflictException();   // someone else saved first, or the client sent no version
        }
        note.edit(body.title().trim(), orEmpty(body.body()));
        return NoteView.of(notes.saveAndFlush(note));   // flush now, so a lost update surfaces as an exception here
    }

    public void delete(long ownerId, long id) {
        notes.delete(owned(ownerId, id));
    }

    /** Someone else's note looks exactly like a missing one: the API never confirms that it exists. */
    private Note owned(long ownerId, long id) {
        return notes.findByIdAndOwnerId(id, ownerId).orElseThrow(NoteNotFoundException::new);
    }

    private static String orEmpty(String text) {
        return text == null ? "" : text;
    }

    static String likePattern(String query) {
        String q = query == null ? "" : query.trim().toLowerCase(Locale.ROOT);
        String escaped = q.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_");
        return "%" + escaped + "%";
    }
}
