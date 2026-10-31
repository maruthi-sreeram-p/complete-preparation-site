@more
## Testing AWS code locally

Tests that need a real AWS account are slow, and they cost money. Tests that mock everything miss real behaviour. Containers give a useful middle ground.

| Test type | Tool | Catches |
|---|---|---|
| Unit | Mock your own interface | Your logic |
| Integration | LocalStack, Testcontainers | Wrong API calls, serialisation |
| Contract or smoke | A real AWS test account | IAM, real limits, real behaviour |

### LocalStack with Testcontainers

```java An SQS and S3 integration test
@SpringBootTest
@Testcontainers
class InvoiceFlowTest {

    @Container
    static LocalStackContainer localstack = new LocalStackContainer(
            DockerImageName.parse("localstack/localstack:3.8"))
        .withServices(LocalStackContainer.Service.S3, LocalStackContainer.Service.SQS);

    @DynamicPropertySource
    static void aws(DynamicPropertyRegistry r) {
        r.add("spring.cloud.aws.endpoint", () -> localstack.getEndpoint().toString());
        r.add("spring.cloud.aws.region.static", localstack::getRegion);
        r.add("spring.cloud.aws.credentials.access-key", localstack::getAccessKey);
        r.add("spring.cloud.aws.credentials.secret-key", localstack::getSecretKey);
    }

    @Autowired SqsTemplate sqs;
    @Autowired S3Client s3;

    @Test
    void messageProducesInvoiceInS3() {
        s3.createBucket(b -> b.bucket("invoices"));
        sqs.send("invoice-events", new InvoiceEvent(42L));

        await().atMost(Duration.ofSeconds(10)).untilAsserted(() ->
            assertThat(s3.listObjectsV2(b -> b.bucket("invoices")).contents()).hasSize(1));
    }
}
```

Note the use of Awaitility: the listener runs asynchronously, so a sleep would be flaky. The queue must also exist before listeners start, so create it in an init script or a configuration bean.

Check LocalStack's current licensing and image terms, since features and availability vary, and use a pinned image version.

### What local tests can't tell you

LocalStack doesn't fully enforce IAM by default, and its behaviour can differ from AWS in edge cases, such as limits. Keep a small set of smoke tests running against a real account after deployment: does the role actually have access? does the queue trigger the worker?

### Testing failure paths

Most cloud bugs are in failure handling, and few people test that. Worth testing:

| Failure | Test |
|---|---|
| Duplicate message | Deliver twice; assert one effect |
| Poison message | Assert that it ends up in the DLQ |
| Throttling | Inject errors using WireMock |
| Database failover | Restart the container in a Testcontainers test; check the pool recovers |
| Slow dependency | Toxiproxy adds latency; assert timeouts work |

```java Asserting idempotency
@Test
void duplicateMessageHasOneEffect() {
    InvoiceEvent event = new InvoiceEvent(42L, "evt-1");
    listener.onMessage(event);
    listener.onMessage(event);
    assertThat(invoices.countByOrder(42L)).isEqualTo(1);
}
```

### Chaos in production-like environments

AWS Fault Injection Service can stop tasks or add latency on purpose. The aim is to learn before a real failure does: does the service recover, do alarms fire, and does the on-call person know what to do? Start in staging, with a clear hypothesis and a stop condition.

!keypoints Test against containers, then smoke test in AWS ;; Use Awaitility rather than sleep ;; Test failure handling explicitly ;; LocalStack doesn't prove your IAM works

?? Your tests pass on LocalStack, but production gets Access Denied. Why?
=> LocalStack doesn't fully enforce IAM. Add smoke tests in a real account.
?? Why is Thread.sleep a poor way to wait for an async result?
=> Too short is flaky, and too long is slow. Awaitility polls until the condition holds or a timeout passes.

## Streaming on AWS: MSK, Kinesis and EventBridge

### MSK from Spring Boot

Your Kafka guide applies almost entirely. What changes is connection and authentication.

```properties Kafka client with IAM authentication
spring.kafka.bootstrap-servers=${MSK_BROKERS}
spring.kafka.properties.security.protocol=SASL_SSL
spring.kafka.properties.sasl.mechanism=AWS_MSK_IAM
spring.kafka.properties.sasl.jaas.config=software.amazon.msk.auth.iam.IAMLoginModule required;
spring.kafka.properties.sasl.client.callback.handler.class=software.amazon.msk.auth.iam.IAMClientCallbackHandler
```

This needs the `aws-msk-iam-auth` library, and a task role allowing actions such as `kafka-cluster:Connect` and read or write on the topic. No passwords are involved.

### Kinesis compared with Kafka

| | Kinesis Data Streams | Kafka (MSK) |
|---|---|---|
| Unit of parallelism | Shard | Partition |
| Throughput per unit | Fixed per shard (about 1 MB/s in) | Depends on brokers |
| Retention | Default 24 hours, can extend | Configurable, long |
| Operations | Very little | More: brokers, storage, upgrades |
| Ecosystem | AWS integrations | Connect, Streams, wide community |
| Portability | AWS only | Standard Kafka |

**Firehose** delivers stream data to S3 or other destinations in batches, with no consumer code, which suits log and analytics pipelines.

### EventBridge from Java

```java Publishing a domain event
eventBridge.putEvents(r -> r.entries(PutEventsRequestEntry.builder()
    .eventBusName("orders")
    .source("com.acme.orders")
    .detailType("OrderPlaced")
    .detail(json.write(new OrderPlaced(9001L, new BigDecimal("499.00"))))
    .build()));
```

```json A rule that matches large orders
{
  "source": ["com.acme.orders"],
  "detail-type": ["OrderPlaced"],
  "detail": { "total": [{ "numeric": [">", 10000] }] }
}
```

`PutEvents` can partly fail, and returns a count of failed entries, so check `failedEntryCount`. EventBridge has **Archive and Replay**, which can resend past events to a bus for recovery.

### Designing events

| Style | Contains | Trade-off |
|---|---|---|
| Thin event | IDs only | Consumers must call back, creating coupling and load |
| Fat event | The data consumers need | Larger, and exposes more of your data |

Most systems use a middle ground: enough for common consumers, and an ID for the rest. Name events in the past tense, such as `OrderPlaced`, since they state facts. Publish a schema, and treat it as a public API.

### Choosing partition keys

For Kafka and Kinesis, the key decides both ordering and load balance. Use `orderId` when events for an order must stay in order. Avoid a low-cardinality key, such as country, as one big value creates a hot shard, while the others sit idle.

### Sending email with SES

```java Sending through SES
ses.sendEmail(r -> r
    .fromEmailAddress("no-reply@example.com")
    .destination(d -> d.toAddresses(user.email()))
    .content(c -> c.simple(s -> s
        .subject(t -> t.data("Your order is confirmed"))
        .body(b -> b.text(t -> t.data(bodyText))))));
```

New accounts begin in a sandbox, where only verified addresses can receive mail. Set up SPF, DKIM and DMARC for deliverability, and watch bounces and complaints, as high rates can suspend your account. Send from a worker, so that an email problem doesn't fail the order.

!keypoints MSK uses IAM auth through a library ;; Kinesis costs less effort, Kafka gives more ;; Check for partial failures in PutEvents ;; Events are a public API

?? Your event carries only an order ID, and five consumers call back the orders API. What's the downside?
=> Coupling and extra load on that API. Include commonly needed data in the event.
?? Why isn't country a good partition key?
=> Few values and uneven sizes create hot partitions.
?? Your app's emails only reach some addresses in a new AWS account. Why?
=> SES starts in a sandbox, which delivers only to verified addresses, until you request production access.
