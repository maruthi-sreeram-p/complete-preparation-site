package dev.javatrail.notes.note;

import java.util.Optional;

import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

public interface NoteRepository extends JpaRepository<Note, Long> {

    Optional<Note> findByIdAndOwnerId(Long id, Long ownerId);

    /** The pattern arrives already escaped, so a search for "100%" matches a literal percent sign. */
    @Query("""
        select n from Note n
        where n.ownerId = :owner
          and (lower(n.title) like :pattern escape '\\' or lower(n.body) like :pattern escape '\\')
        """)
    Page<Note> search(@Param("owner") Long owner, @Param("pattern") String pattern, Pageable pageable);
}
