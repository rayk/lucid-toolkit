# Data Modeling

LCA data strategy: Single Subject Types internally, Schema.org at boundaries.

## Internal Modeling: Single Subject Types

### Principle

Internal data structures are minimal, focused types designed for specific computations. They contain exactly the data needed and nothing more.

### Pattern

```typescript
// ❌ Bad: Bloated internal type
interface Order {
  id: string;
  orderNumber: string;
  customer: Customer;
  items: OrderItem[];
  shippingAddress: Address;
  billingAddress: Address;
  paymentMethod: PaymentMethod;
  status: OrderStatus;
  createdAt: Date;
  updatedAt: Date;
  metadata: Record<string, unknown>;
  // ... 20 more fields
}

// ✅ Good: Single Subject Types for specific operations
interface OrderForPricing {
  items: { quantity: number; unitPrice: number }[];
  discountCode?: string;
}

interface OrderForValidation {
  customerId: string;
  items: { productId: string; quantity: number }[];
}

interface OrderForShipping {
  shippingAddress: Address;
  items: { weight: number; dimensions: Dimensions }[];
}
```

### Benefits

- Functions receive exactly what they need
- Easier to test (smaller input surface)
- Clearer contracts between components
- No accidental coupling to unrelated fields

## Boundary Modeling: Schema.org

### Principle

At system edges—APIs, AI agents, LLMs—use Schema.org types for semantic interoperability. Systems become self-describing to automated consumers.

### Schema.org Types for Common Domains

| Domain | Schema.org Type | Use Case |
|--------|-----------------|----------|
| Products | `schema.org/Product` | E-commerce catalogs |
| Orders | `schema.org/Order` | Order management |
| People | `schema.org/Person` | User profiles |
| Organizations | `schema.org/Organization` | Business entities |
| Events | `schema.org/Event` | Calendaring |
| Places | `schema.org/Place` | Location data |
| Actions | `schema.org/Action` | Activity tracking |

### JSON-LD Serialization

```json
{
  "@context": "https://schema.org",
  "@type": "Order",
  "@id": "urn:order:12345",
  "orderNumber": "ORD-12345",
  "orderDate": "2025-01-15T10:00:00Z",
  "orderStatus": "OrderProcessing",
  "customer": {
    "@type": "Person",
    "@id": "urn:customer:67890",
    "name": "Jane Smith"
  },
  "orderedItem": [
    {
      "@type": "OrderItem",
      "orderQuantity": 2,
      "orderedItem": {
        "@type": "Product",
        "@id": "urn:product:ABC",
        "name": "Widget"
      }
    }
  ]
}
```

### Extension Mechanism

When Schema.org doesn't cover your domain:

```json
{
  "@context": [
    "https://schema.org",
    {
      "acme": "https://acme.com/vocab#",
      "internalSku": "acme:internalSku",
      "warehouseLocation": "acme:warehouseLocation"
    }
  ],
  "@type": "Product",
  "name": "Widget",
  "internalSku": "WDG-001",
  "warehouseLocation": "A-15-3"
}
```

## The Mapping Layer

### Principle

A specific set of pure functions transforms efficient internal types to Schema.org equivalents at egress Conduits.

### Pattern

```typescript
// Internal type (Single Subject)
interface InternalOrder {
  id: string;
  num: string;
  ts: number;
  custId: string;
  items: { pid: string; qty: number; price: number }[];
}

// Schema.org type (Boundary)
interface SchemaOrder {
  '@context': 'https://schema.org';
  '@type': 'Order';
  '@id': string;
  orderNumber: string;
  orderDate: string;
  customer: { '@type': 'Person'; '@id': string };
  orderedItem: SchemaOrderItem[];
}

// Mapping function (pure)
function toSchemaOrder(internal: InternalOrder): SchemaOrder {
  return {
    '@context': 'https://schema.org',
    '@type': 'Order',
    '@id': `urn:order:${internal.id}`,
    orderNumber: internal.num,
    orderDate: new Date(internal.ts).toISOString(),
    customer: {
      '@type': 'Person',
      '@id': `urn:customer:${internal.custId}`
    },
    orderedItem: internal.items.map(toSchemaOrderItem)
  };
}
```

### Bidirectional Mapping

```typescript
// Ingress mapping (Schema.org → Internal)
function fromSchemaOrder(schema: SchemaOrder): InternalOrder {
  return {
    id: extractId(schema['@id']),
    num: schema.orderNumber,
    ts: new Date(schema.orderDate).getTime(),
    custId: extractId(schema.customer['@id']),
    items: schema.orderedItem.map(fromSchemaOrderItem)
  };
}

// Helper
function extractId(urn: string): string {
  return urn.split(':').pop()!;
}
```

## Graph-Based Thinking

### Principle

Data conceptualized as graph of interconnected entities, not rigid tables. Relationships are first-class citizens.

### Node and Edge Pattern

```typescript
// Graph node representation
interface GraphNode {
  id: string;
  type: string;
  properties: Record<string, unknown>;
}

// Graph edge representation
interface GraphEdge {
  from: string;
  to: string;
  type: string;
  properties?: Record<string, unknown>;
}

// Domain as graph
const orderGraph = {
  nodes: [
    { id: 'order:123', type: 'Order', properties: { num: 'ORD-123' } },
    { id: 'customer:456', type: 'Person', properties: { name: 'Jane' } },
    { id: 'product:789', type: 'Product', properties: { name: 'Widget' } }
  ],
  edges: [
    { from: 'order:123', to: 'customer:456', type: 'orderedBy' },
    { from: 'order:123', to: 'product:789', type: 'contains', properties: { qty: 2 } }
  ]
};
```

### Query Pattern

```typescript
// Graph query interface
interface GraphQuery {
  startNode(id: string): GraphQuery;
  followEdge(type: string): GraphQuery;
  filterByType(type: string): GraphQuery;
  get(): GraphNode[];
}

// Usage
const customerOrders = graph
  .startNode('customer:456')
  .followEdge('ordered')
  .filterByType('Order')
  .get();
```

## Data Strategy Checklist

- [ ] Internal types are Single Subject (minimal for their purpose)
- [ ] Boundary types use Schema.org vocabulary
- [ ] Mapping layer exists as pure functions
- [ ] Extensions use standard mechanisms (not proprietary roots)
- [ ] Relationships modeled explicitly (graph thinking)
- [ ] No Schema.org bloat in internal computations
