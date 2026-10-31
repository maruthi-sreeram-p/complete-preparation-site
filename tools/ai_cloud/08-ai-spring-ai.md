@part ai-spring | AI Part 3: LLMs from Spring Boot with Spring AI | ai
## Setting up Spring AI and ChatClient

Spring AI gives you a portable API over model providers, in normal Spring style. LangChain4j is the main alternative, and the ideas are the same. The examples follow the Spring AI 2.0 documentation.

```xml pom.xml: import the BOM, then add a provider starter
<dependencyManagement>
  <dependencies>
    <dependency>
      <groupId>org.springframework.ai</groupId>
      <artifactId>spring-ai-bom</artifactId>
      <version>${spring-ai.version}</version>
      <type>pom</type>
      <scope>import</scope>
    </dependency>
  </dependencies>
</dependencyManagement>

<dependencies>
  <dependency>
    <groupId>org.springframework.ai</groupId>
    <artifactId>spring-ai-starter-model-anthropic</artifactId> <!-- or -model-openai and others -->
  </dependency>
</dependencies>
```

```properties The key comes from the environment
spring.ai.anthropic.api-key=${ANTHROPIC_API_KEY}
```

Take model names and property names from current documentation, as they change often.

### A first call

```java ChatClient, injected through its builder
@RestController
class AskController {

    private final ChatClient chat;

    AskController(ChatClient.Builder builder) {
        this.chat = builder
            .defaultSystem("You are a concise assistant for Java developers.")
            .build();
    }

    @GetMapping("/api/ask")
    String ask(@RequestParam String q) {
        return chat.prompt()
            .user(q)
            .call()
            .content();
    }
}
```

The fluent call builds a prompt, sends it when a terminal method such as `content()` runs, and returns the text. Remember what this is: a slow remote call, not a method on your object.

### Prompt templates

```java A template with parameters
String reply = chat.prompt()
    .user(u -> u.text("Summarise this ticket in {count} points: {ticket}")
        .param("count", 3)
        .param("ticket", ticketText))
    .call()
    .content();
```

### Advisors

An **advisor** wraps a call, much like a servlet filter: it can change the request, or inspect the response. Spring AI uses advisors for memory and RAG, and you can write your own for logging.

```mermaid Advisors wrap the model call
flowchart LR
  A[Your code] --> B[Memory advisor]
  B --> C[RAG advisor]
  C --> D[Model]
  D --> C
  C --> B
  B --> A
```

!keypoints Inject ChatClient.Builder, and let configuration choose the provider ;; A terminal method sends the request ;; Keep keys in the environment ;; Advisors are filters around the model call

?? Why inject ChatClient.Builder rather than creating a provider client?
=> Configuration chooses the model, so you can switch providers, and tests can substitute it.
?? When is the request actually sent?
=> When a terminal method such as `content()`, `entity()` or `chatResponse()` runs on the call spec.

## Structured output and streaming

### Mapping to Java types

```java A real feature in a few lines
@Service
class TicketTriage {

    enum Category { BILLING, BUG, OTHER }

    record Triage(Category category, int priority, String summary) {}

    private final ChatClient chat;

    TicketTriage(ChatClient.Builder builder) {
        this.chat = builder
            .defaultSystem("You triage support tickets for a bookstore. Priority is 1 (urgent) to 3 (low).")
            .build();
    }

    Triage triage(String ticket) {
        Triage t = chat.prompt().user(ticket).call().entity(Triage.class);
        if (t == null || t.priority() < 1 || t.priority() > 3) {
            throw new InvalidModelOutput("bad triage result");
        }
        return t;
    }
}
```

`entity()` adds format instructions, and converts the reply. A typed result can still be wrong, so validate the values. An enum narrows what the model may return. For lists, use `new ParameterizedTypeReference<List<Triage>>() {}`.

### Streaming to the browser

Users dislike waiting ten seconds at a blank screen. Streaming shows text as it is generated.

```java Server-sent events
@GetMapping(value = "/api/chat", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
Flux<String> chat(@RequestParam String message) {
    return chat.prompt().user(message).stream().content();
}
```

```javascript Reading a stream in React
const res = await fetch(`/api/chat?message=${encodeURIComponent(text)}`);
const reader = res.body.pipeThrough(new TextDecoderStream()).getReader();
while (true) {
  const { value, done } = await reader.read();
  if (done) break;
  setAnswer((a) => a + value);
}
```

This raw reader is simplified, since SSE frames include `data:` prefixes that real code must parse. Use POST for real messages, because URLs get logged. Streaming complicates validation, as you can't check an answer before showing it, so stream only free text, not structured results.

!keypoints entity() maps replies to records ;; Validate values, not only shape ;; Stream long text ;; Do not stream what must be validated first

?? Why shouldn't you trust a typed result?
=> The type checks shape, not truth. A model can return a valid but wrong value, so check ranges and business rules.
?? Why avoid sending chat messages through GET parameters in production?
=> URLs end up in access logs and browser history, and may contain personal data.

## Chat memory

The model is stateless, so conversations need your code to resend history. Spring AI's `ChatMemory` decides what to keep, and a `ChatMemoryRepository` stores it.

```java Memory through an advisor
@Service
class Assistant {

    private final ChatClient chat;

    Assistant(ChatClient.Builder builder, ChatMemory memory) {
        this.chat = builder
            .defaultAdvisors(MessageChatMemoryAdvisor.builder(memory).build())
            .build();
    }

    String reply(String userId, String sessionId, String message) {
        String conversationId = userId + ":" + sessionId;   // scoped on the server
        return chat.prompt()
            .user(message)
            .advisors(a -> a.param(ChatMemory.CONVERSATION_ID, conversationId))
            .call()
            .content();
    }
}
```

Spring AI auto-configures a `MessageWindowChatMemory`, which keeps recent messages, with an in-memory repository by default. Use `JdbcChatMemoryRepository` or a similar store for anything that must survive a restart or be shared across instances.

!warning Never trust a client-supplied conversation ID :: The conversation ID is the only thing separating users' messages. Build it on the server from the authenticated user. If a client can send any ID, one user can read another's conversation.

Chat **memory** is what the model sees, and should stay short. Chat **history** is your full record, for audit or display. Store them separately, using normal tables for history.

Strategies for long conversations: keep the last N messages, summarise older ones, or store facts and retrieve them when needed. Each choice trades cost against recall.

!keypoints Memory is your job ;; Scope conversation IDs on the server ;; In-memory storage does not survive a restart ;; Memory and history are different things

?? Why can in-memory chat memory break behind a load balancer?
=> Each instance holds its own messages, so the next request may land where the history isn't. Use a shared repository.
?? A user sends conversationId=123 and sees someone else's chat. What is the fix?
=> Derive the ID on the server from the authenticated user, and check ownership.

## Treating the model as a remote dependency

Everything you know about remote calls applies, and the failure modes are sharper: seconds of latency, rate limits, and a bill per request.

| Concern | Approach |
|---|---|
| Timeouts | Set explicitly on the HTTP client; a stuck call holds a thread |
| Retries | Only on rate limits and transient errors, with backoff; Spring AI has retry settings |
| Concurrency | Limit it with a bulkhead, so that AI calls cannot take every thread |
| Transactions | Never hold a database transaction during a model call |
| Cost | Log tokens per feature and user; set per-user limits |
| Fallback | The product should still work when the model is down |
| Privacy | Know what you send, remove what isn't needed, and check provider terms |

```java Do the slow call outside the transaction
public Summary summarise(long ticketId) {
    Ticket ticket = tickets.load(ticketId);                 // short read
    String text = chat.prompt().user(ticket.body()).call().content();   // seconds, no transaction
    return tickets.saveSummary(ticketId, text);             // short @Transactional write
}
```

With Java 21, virtual threads make blocking calls much cheaper, so plain MVC handles many concurrent model calls without reactive code. You still need limits, as the provider's rate limit and your budget remain.

### Testing

- **Unit tests:** mock `ChatModel`, or wrap the AI call behind your own interface and mock that. Test your validation and fallback logic.
- **Evaluation tests:** run a scored set of real questions, separately from normal builds, since they cost money and vary.
- **Failure tests:** simulate timeouts and rate limits. WireMock works well for this.

### Spring AI or LangChain4j?

Both are capable. Spring AI fits naturally if you are already on Spring Boot. LangChain4j predates it and is framework-independent. Interviewers care far more about the concepts than about which library you used.

!interview Interview answer :: **"What happens to your app if the LLM provider is down?"** Calls time out quickly, a circuit breaker stops further attempts, and the feature degrades: a clear message, or a fallback such as ordinary search. The rest of the app is unaffected, because a bulkhead limits AI concurrency.

!keypoints Timeouts, limits and fallbacks ;; Never hold a transaction open during a model call ;; Track tokens per feature and user ;; Test failure paths

?? Why not call the model inside @Transactional?
=> The call can take many seconds, so it holds a connection and locks, and it can exhaust the pool.
?? How do you unit test code that calls a model?
=> Mock the model, and test validation, retries and fallbacks. Measure quality separately with an evaluation set.
