package dev.javatrail.notes.note;

import java.time.Instant;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import jakarta.persistence.Version;

@Entity
@Table(name = "notes")
public class Note {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "owner_id", nullable = false, updatable = false)
    private Long ownerId;

    @Column(nullable = false, length = 120)
    private String title;

    @Column(nullable = false, length = 5000)
    private String body;

    /** Hibernate raises an exception if two writers update the same version. */
    @Version
    private long version;

    @Column(name = "created_at", nullable = false, updatable = false)
    private Instant createdAt = Instant.now();

    @Column(name = "updated_at", nullable = false)
    private Instant updatedAt = Instant.now();

    protected Note() {}   // for JPA

    public Note(Long ownerId, String title, String body) {
        this.ownerId = ownerId;
        this.title = title;
        this.body = body;
    }

    public void edit(String title, String body) {
        this.title = title;
        this.body = body;
        this.updatedAt = Instant.now();
    }

    public Long getId() { return id; }
    public Long getOwnerId() { return ownerId; }
    public String getTitle() { return title; }
    public String getBody() { return body; }
    public long getVersion() { return version; }
    public Instant getUpdatedAt() { return updatedAt; }
    public Instant getCreatedAt() { return createdAt; }
}
