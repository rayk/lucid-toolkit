# Communication Protocols
<!-- Status: Draft -->
<!-- Last Updated: YYYY-MM-DD -->

The verbs of the system—how components communicate.

## Transport Protocols

| Protocol | Use Case | Direction | Services |
|----------|----------|-----------|----------|
| gRPC | Internal sync calls | Service ↔ Service | All internal |
| REST/HTTP | External APIs | Client → Service | Public-facing |
| Kafka | Async events | Service → Bus → Service | Event-driven |
| WebSocket | Real-time updates | Service ↔ Client | Notifications |

## Serialization Formats

| Format | Use Case | Schema Location | Validation |
|--------|----------|-----------------|------------|
| Protocol Buffers | gRPC messages | `protos/` | Compile-time |
| JSON | REST APIs | OpenAPI specs | Runtime |
| Avro | Kafka events | Schema Registry | Registry |

## Message Structures

### Sync Request/Response (gRPC)

```protobuf
// Standard request envelope
message Request {
  string request_id = 1;      // Unique request identifier
  string correlation_id = 2;  // For request tracing
  google.protobuf.Timestamp timestamp = 3;

  // Payload varies by operation
}

// Standard response envelope
message Response {
  string request_id = 1;
  oneof result {
    SuccessPayload success = 2;
    ErrorPayload error = 3;
  }
}

message ErrorPayload {
  string code = 1;
  string message = 2;
  repeated FieldError details = 3;
}
```

### Async Events (Schema.org)

```json
{
  "@context": "https://schema.org",
  "@type": "Action",
  "@id": "urn:event:{event-id}",
  "actionStatus": "CompletedActionStatus",
  "agent": {
    "@type": "SoftwareApplication",
    "@id": "urn:service:{service-name}"
  },
  "object": {
    "@type": "{EntityType}",
    "@id": "urn:{entity}:{entity-id}"
  },
  "startTime": "2025-01-15T10:00:00Z",
  "endTime": "2025-01-15T10:00:01Z"
}
```

### REST Response (Schema.org)

```json
{
  "@context": "https://schema.org",
  "@type": "{EntityType}",
  "@id": "urn:{entity}:{id}",
  "identifier": "{id}",
  "name": "{name}",
  "dateCreated": "2025-01-15T10:00:00Z",
  "dateModified": "2025-01-15T10:00:00Z"
}
```

## Versioning Strategy

### API Versioning

- **Method**: URL path versioning
- **Format**: `/v{major}/resource`
- **Policy**: Support N-1 versions minimum

| Version | Status | Sunset Date |
|---------|--------|-------------|
| v2 | Current | - |
| v1 | Deprecated | 2025-06-01 |

### Event Versioning

- **Method**: Schema Registry with compatibility
- **Compatibility**: BACKWARD (consumers can read old events)
- **Evolution**: Add optional fields only

### Proto Versioning

- **Method**: Package versioning
- **Format**: `service.v1`, `service.v2`
- **Policy**: Breaking changes require new version

## Error Codes

Standard error codes across all protocols.

| Code | HTTP | gRPC | Meaning | Retry |
|------|------|------|---------|-------|
| `INVALID_ARGUMENT` | 400 | 3 | Bad input | No |
| `UNAUTHENTICATED` | 401 | 16 | No/bad credentials | No |
| `PERMISSION_DENIED` | 403 | 7 | Not authorized | No |
| `NOT_FOUND` | 404 | 5 | Resource missing | No |
| `ALREADY_EXISTS` | 409 | 6 | Duplicate | No |
| `RESOURCE_EXHAUSTED` | 429 | 8 | Rate limited | Yes |
| `INTERNAL` | 500 | 13 | Server error | Yes |
| `UNAVAILABLE` | 503 | 14 | Service down | Yes |

## Related Documents

- [Shared Concepts](shared-concepts.md) - The entities being transmitted
- [Integration Patterns](integration-patterns.md) - How communications flow end-to-end
- [Cross-Cutting Concerns](cross-cutting-concerns.md) - Auth headers, tracing

---

*Communication protocols - the verbs of the system*
