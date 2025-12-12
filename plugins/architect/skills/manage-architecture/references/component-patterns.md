# Component Patterns

Implementation patterns for LCA structural components.

## Atom Patterns

### Pure Function Pattern

```typescript
// ✅ Good: Pure function Atom
function calculatePrice(quantity: number, unitPrice: number): number {
  return quantity * unitPrice;
}

// ❌ Bad: Impure function (side effects)
function calculateAndLogPrice(quantity: number, unitPrice: number): number {
  console.log(`Calculating price...`); // Side effect!
  return quantity * unitPrice;
}
```

### Value Object Pattern

```typescript
// ✅ Good: Immutable value object
class Money {
  private constructor(
    readonly amount: number,
    readonly currency: string
  ) {}

  static of(amount: number, currency: string): Money {
    return new Money(amount, currency);
  }

  add(other: Money): Money {
    if (this.currency !== other.currency) {
      throw new Error('Currency mismatch');
    }
    return Money.of(this.amount + other.amount, this.currency);
  }
}
```

### Validator Pattern

```typescript
// ✅ Good: Pure validation Atom
type ValidationResult = { valid: true } | { valid: false; errors: string[] };

function validateOrder(order: OrderInput): ValidationResult {
  const errors: string[] = [];

  if (order.quantity <= 0) {
    errors.push('Quantity must be positive');
  }
  if (!order.productId) {
    errors.push('Product ID required');
  }

  return errors.length === 0
    ? { valid: true }
    : { valid: false, errors };
}
```

## Composite Patterns

### Orchestrator Pattern

```typescript
// ✅ Good: Composite orchestrates Atoms
class OrderProcessor {
  constructor(
    private readonly validator: OrderValidator,
    private readonly calculator: PriceCalculator,
    private readonly formatter: OrderFormatter
  ) {}

  process(input: OrderInput): ProcessedOrder {
    // Orchestration only - no business logic here
    const validation = this.validator.validate(input);
    if (!validation.valid) {
      throw new ValidationError(validation.errors);
    }

    const price = this.calculator.calculate(input);
    return this.formatter.format(input, price);
  }
}
```

### Lifecycle Manager Pattern

```typescript
// ✅ Good: Composite manages lifecycles
class ServiceHost {
  private readonly services: Service[] = [];

  register(service: Service): void {
    this.services.push(service);
  }

  async start(): Promise<void> {
    for (const service of this.services) {
      await service.start();
    }
  }

  async stop(): Promise<void> {
    for (const service of this.services.reverse()) {
      await service.stop();
    }
  }
}
```

## Conduit Patterns

### Versioned API Pattern

```protobuf
// ✅ Good: Versioned Protocol Buffer service
syntax = "proto3";

package order.v1;

service OrderService {
  rpc CreateOrder(CreateOrderRequest) returns (CreateOrderResponse);
  rpc GetOrder(GetOrderRequest) returns (Order);
}

message CreateOrderRequest {
  string product_id = 1;
  int32 quantity = 2;
}
```

### REST Boundary Pattern

```typescript
// ✅ Good: REST controller as Conduit
@Controller('v1/orders')
class OrderControllerV1 {
  constructor(private readonly orderProcessor: OrderProcessor) {}

  @Post()
  async createOrder(@Body() dto: CreateOrderDto): Promise<OrderResponse> {
    // Transform external DTO → internal type
    const input = this.toInternal(dto);

    // Delegate to Composite
    const result = await this.orderProcessor.process(input);

    // Transform internal → Schema.org response
    return this.toSchemaOrg(result);
  }

  private toInternal(dto: CreateOrderDto): OrderInput {
    // Mapping layer
  }

  private toSchemaOrg(result: ProcessedOrder): OrderResponse {
    // Schema.org/Order mapping
  }
}
```

### Event Boundary Pattern

```typescript
// ✅ Good: Event publisher as Conduit
interface OrderCreatedEvent {
  '@type': 'Order';
  '@id': string;
  orderNumber: string;
  orderDate: string;
  customer: { '@type': 'Person'; '@id': string };
}

class OrderEventPublisher {
  constructor(private readonly bus: EventBus) {}

  async publishCreated(order: InternalOrder): Promise<void> {
    const event: OrderCreatedEvent = {
      '@type': 'Order',
      '@id': `urn:order:${order.id}`,
      orderNumber: order.number,
      orderDate: order.createdAt.toISOString(),
      customer: {
        '@type': 'Person',
        '@id': `urn:customer:${order.customerId}`
      }
    };

    await this.bus.publish('order.created.v1', event);
  }
}
```

## Anti-Patterns

### Behavior Inheritance (Avoid)

```typescript
// ❌ Bad: Inheritance for behavior
class BaseEntity {
  validate(): boolean {
    // Shared validation logic
  }
}

class Order extends BaseEntity {
  // Inherits validate behavior
}

// ✅ Good: Composition instead
class Order {
  constructor(private readonly validator: EntityValidator) {}

  validate(): boolean {
    return this.validator.validate(this);
  }
}
```

### Logic in Composite (Avoid)

```typescript
// ❌ Bad: Business logic in Composite
class OrderProcessor {
  process(order: Order): ProcessedOrder {
    // Business logic should be in Atom!
    const discount = order.quantity > 10 ? 0.1 : 0;
    const price = order.quantity * order.unitPrice * (1 - discount);
    return { ...order, price };
  }
}

// ✅ Good: Extract to Atom
class OrderProcessor {
  constructor(private readonly calculator: PriceCalculator) {}

  process(order: Order): ProcessedOrder {
    const price = this.calculator.calculate(order); // Atom
    return { ...order, price };
  }
}
```

### Unversioned Conduit (Avoid)

```typescript
// ❌ Bad: No versioning
@Controller('orders')
class OrderController { }

// ✅ Good: Versioned
@Controller('v1/orders')
class OrderControllerV1 { }
```
