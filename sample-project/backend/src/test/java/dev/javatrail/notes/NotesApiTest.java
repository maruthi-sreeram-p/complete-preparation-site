package dev.javatrail.notes;

import static org.hamcrest.Matchers.containsString;
import static org.hamcrest.Matchers.hasSize;
import static org.hamcrest.Matchers.is;
import static org.hamcrest.Matchers.not;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.delete;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.put;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.cookie;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.header;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import java.util.UUID;

import com.jayway.jsonpath.JsonPath;

import jakarta.servlet.http.Cookie;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc;
import org.springframework.http.MediaType;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;

@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
class NotesApiTest {

    @Autowired
    MockMvc mvc;

    // ---------------------------------------------------------------- helpers

    private static String uniqueEmail() {
        return "user-" + UUID.randomUUID() + "@example.com";
    }

    private Cookie register(String email) throws Exception {
        MvcResult result = mvc.perform(post("/api/auth/register")
                .contentType(MediaType.APPLICATION_JSON)
                .content("""
                    {"email": "%s", "password": "correct-horse"}""".formatted(email)))
            .andExpect(status().isCreated())
            .andReturn();
        return result.getResponse().getCookie("notes_token");
    }

    private long createNote(Cookie user, String title, String body) throws Exception {
        MvcResult result = mvc.perform(post("/api/notes")
                .cookie(user)
                .contentType(MediaType.APPLICATION_JSON)
                .content("""
                    {"title": "%s", "body": "%s"}""".formatted(title, body)))
            .andExpect(status().isCreated())
            .andReturn();
        return ((Number) JsonPath.read(result.getResponse().getContentAsString(), "$.id")).longValue();
    }

    // ---------------------------------------------------------------- authentication

    @Test
    void registrationSetsAnHttpOnlySameSiteStrictCookie() throws Exception {
        mvc.perform(post("/api/auth/register")
                .contentType(MediaType.APPLICATION_JSON)
                .content("""
                    {"email": "  Asha@Example.com ", "password": "correct-horse"}"""))
            .andExpect(status().isCreated())
            .andExpect(cookie().httpOnly("notes_token", true))
            .andExpect(header().string("Set-Cookie", containsString("SameSite=Strict")))
            .andExpect(jsonPath("$.email", is("asha@example.com")))
            .andExpect(jsonPath("$.password").doesNotExist());
    }

    @Test
    void duplicateEmailIsRejectedWithAFieldError() throws Exception {
        String email = uniqueEmail();
        register(email);
        mvc.perform(post("/api/auth/register")
                .contentType(MediaType.APPLICATION_JSON)
                .content("""
                    {"email": "%s", "password": "correct-horse"}""".formatted(email.toUpperCase())))
            .andExpect(status().isConflict())
            .andExpect(jsonPath("$.errors.email").exists());
    }

    @Test
    void weakPasswordsAndBadEmailsAreRejected() throws Exception {
        mvc.perform(post("/api/auth/register")
                .contentType(MediaType.APPLICATION_JSON)
                .content("""
                    {"email": "not-an-email", "password": "short"}"""))
            .andExpect(status().isBadRequest())
            .andExpect(jsonPath("$.errors.email").exists())
            .andExpect(jsonPath("$.errors.password").exists());
    }

    @Test
    void loginSucceedsWithTheRightPasswordAndGivesTheSameAnswerForWrongOnes() throws Exception {
        String email = uniqueEmail();
        register(email);

        mvc.perform(post("/api/auth/login")
                .contentType(MediaType.APPLICATION_JSON)
                .content("""
                    {"email": "%s", "password": "correct-horse"}""".formatted(email)))
            .andExpect(status().isOk())
            .andExpect(cookie().exists("notes_token"));

        String wrongPassword = mvc.perform(post("/api/auth/login")
                .contentType(MediaType.APPLICATION_JSON)
                .content("""
                    {"email": "%s", "password": "wrong-password"}""".formatted(email)))
            .andExpect(status().isUnauthorized())
            .andReturn().getResponse().getContentAsString();

        String unknownUser = mvc.perform(post("/api/auth/login")
                .contentType(MediaType.APPLICATION_JSON)
                .content("""
                    {"email": "nobody-%s@example.com", "password": "correct-horse"}""".formatted(UUID.randomUUID())))
            .andExpect(status().isUnauthorized())
            .andReturn().getResponse().getContentAsString();

        // the response must not reveal whether the account exists
        org.junit.jupiter.api.Assertions.assertEquals(wrongPassword, unknownUser);
    }

    @Test
    void logoutExpiresTheCookie() throws Exception {
        mvc.perform(post("/api/auth/logout"))
            .andExpect(status().isNoContent())
            .andExpect(cookie().maxAge("notes_token", 0));
    }

    @Test
    void protectedEndpointsNeedAToken() throws Exception {
        mvc.perform(get("/api/notes")).andExpect(status().isUnauthorized());
        mvc.perform(get("/api/me")).andExpect(status().isUnauthorized());
        mvc.perform(get("/api/notes").cookie(new Cookie("notes_token", "not-a-real-token")))
            .andExpect(status().isUnauthorized());
    }

    @Test
    void healthEndpointIsPublic() throws Exception {
        mvc.perform(get("/actuator/health")).andExpect(status().isOk());
    }

    @Test
    void meReturnsTheSignedInUser() throws Exception {
        String email = uniqueEmail();
        Cookie user = register(email);
        mvc.perform(get("/api/me").cookie(user))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.email", is(email)));
    }

    // ---------------------------------------------------------------- notes

    @Test
    void createReadUpdateAndDeleteANote() throws Exception {
        Cookie user = register(uniqueEmail());
        long id = createNote(user, "Shopping", "milk");

        mvc.perform(get("/api/notes/" + id).cookie(user))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.title", is("Shopping")))
            .andExpect(jsonPath("$.version", is(0)));

        mvc.perform(put("/api/notes/" + id).cookie(user)
                .contentType(MediaType.APPLICATION_JSON)
                .content("""
                    {"title": "Shopping list", "body": "milk, eggs", "version": 0}"""))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.title", is("Shopping list")))
            .andExpect(jsonPath("$.version", is(1)));

        mvc.perform(delete("/api/notes/" + id).cookie(user)).andExpect(status().isNoContent());
        mvc.perform(get("/api/notes/" + id).cookie(user)).andExpect(status().isNotFound());
    }

    @Test
    void validationErrorsAreReportedPerField() throws Exception {
        Cookie user = register(uniqueEmail());
        mvc.perform(post("/api/notes").cookie(user)
                .contentType(MediaType.APPLICATION_JSON)
                .content("""
                    {"title": "   ", "body": "x"}"""))
            .andExpect(status().isBadRequest())
            .andExpect(jsonPath("$.errors.title").exists());

        mvc.perform(post("/api/notes").cookie(user)
                .contentType(MediaType.APPLICATION_JSON)
                .content("""
                    {"title": "%s"}""".formatted("x".repeat(121))))
            .andExpect(status().isBadRequest())
            .andExpect(jsonPath("$.errors.title").exists());
    }

    @Test
    void aMissingBodyIsStoredAsEmptyText() throws Exception {
        Cookie user = register(uniqueEmail());
        mvc.perform(post("/api/notes").cookie(user)
                .contentType(MediaType.APPLICATION_JSON)
                .content("""
                    {"title": "Only a title"}"""))
            .andExpect(status().isCreated())
            .andExpect(jsonPath("$.body", is("")));
    }

    @Test
    void anotherUsersNoteLooksLikeItDoesNotExist() throws Exception {
        Cookie asha = register(uniqueEmail());
        Cookie ravi = register(uniqueEmail());
        long id = createNote(asha, "Private", "secret");

        mvc.perform(get("/api/notes/" + id).cookie(ravi)).andExpect(status().isNotFound());
        mvc.perform(put("/api/notes/" + id).cookie(ravi)
                .contentType(MediaType.APPLICATION_JSON)
                .content("""
                    {"title": "Hijacked", "body": "", "version": 0}"""))
            .andExpect(status().isNotFound());
        mvc.perform(delete("/api/notes/" + id).cookie(ravi)).andExpect(status().isNotFound());

        mvc.perform(get("/api/notes").cookie(ravi))
            .andExpect(jsonPath("$.content", hasSize(0)));
        mvc.perform(get("/api/notes/" + id).cookie(asha))
            .andExpect(jsonPath("$.title", is("Private")));
    }

    @Test
    void aStaleVersionIsRejectedWithAConflict() throws Exception {
        Cookie user = register(uniqueEmail());
        long id = createNote(user, "Shared", "v0");

        // two browser tabs both loaded version 0
        mvc.perform(put("/api/notes/" + id).cookie(user)
                .contentType(MediaType.APPLICATION_JSON)
                .content("""
                    {"title": "Tab one", "body": "", "version": 0}"""))
            .andExpect(status().isOk());

        mvc.perform(put("/api/notes/" + id).cookie(user)
                .contentType(MediaType.APPLICATION_JSON)
                .content("""
                    {"title": "Tab two", "body": "", "version": 0}"""))
            .andExpect(status().isConflict())
            .andExpect(jsonPath("$.title", is("Edit conflict")));

        mvc.perform(get("/api/notes/" + id).cookie(user))
            .andExpect(jsonPath("$.title", is("Tab one")));
    }

    @Test
    void anUpdateWithoutAVersionIsRejected() throws Exception {
        Cookie user = register(uniqueEmail());
        long id = createNote(user, "Needs version", "");
        mvc.perform(put("/api/notes/" + id).cookie(user)
                .contentType(MediaType.APPLICATION_JSON)
                .content("""
                    {"title": "No version", "body": ""}"""))
            .andExpect(status().isConflict());
    }

    @Test
    void listIsPagedNewestFirstAndSizeIsCapped() throws Exception {
        Cookie user = register(uniqueEmail());
        for (int i = 1; i <= 5; i++) {
            createNote(user, "Note " + i, "");
        }

        mvc.perform(get("/api/notes?size=2&page=0").cookie(user))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.content", hasSize(2)))
            .andExpect(jsonPath("$.content[0].title", is("Note 5")))
            .andExpect(jsonPath("$.page.totalElements", is(5)))
            .andExpect(jsonPath("$.page.totalPages", is(3)));

        mvc.perform(get("/api/notes?size=2&page=2").cookie(user))
            .andExpect(jsonPath("$.content", hasSize(1)))
            .andExpect(jsonPath("$.content[0].title", is("Note 1")));

        mvc.perform(get("/api/notes?size=100000").cookie(user))
            .andExpect(jsonPath("$.page.size", is(100)));

        mvc.perform(get("/api/notes?page=-4&size=0").cookie(user))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.page.number", is(0)));
    }

    @Test
    void searchIsCaseInsensitiveAndTreatsWildcardsAsPlainText() throws Exception {
        Cookie user = register(uniqueEmail());
        createNote(user, "Java Notes", "streams and lambdas");
        createNote(user, "Budget", "saved 100% of the target");
        createNote(user, "Other", "nothing relevant");

        mvc.perform(get("/api/notes?q=JAVA").cookie(user))
            .andExpect(jsonPath("$.content", hasSize(1)))
            .andExpect(jsonPath("$.content[0].title", is("Java Notes")));

        mvc.perform(get("/api/notes?q=lambdas").cookie(user))
            .andExpect(jsonPath("$.content", hasSize(1)));

        mvc.perform(get("/api/notes").param("q", "100%").cookie(user))
            .andExpect(jsonPath("$.content", hasSize(1)))
            .andExpect(jsonPath("$.content[0].title", is("Budget")));

        // a bare % must not match everything
        mvc.perform(get("/api/notes").param("q", "%").cookie(user))
            .andExpect(jsonPath("$.content", hasSize(1)));
        mvc.perform(get("/api/notes").param("q", "_").cookie(user))
            .andExpect(jsonPath("$.content", hasSize(0)));
    }

    @Test
    void errorResponsesNeverLeakInternals() throws Exception {
        Cookie user = register(uniqueEmail());
        mvc.perform(get("/api/notes/not-a-number").cookie(user))
            .andExpect(status().is4xxClientError())
            .andExpect(jsonPath("$.trace").doesNotExist())
            .andExpect(content().string(not(containsString("Exception"))));
    }

    private static org.springframework.test.web.servlet.result.ContentResultMatchers content() {
        return org.springframework.test.web.servlet.result.MockMvcResultMatchers.content();
    }
}
