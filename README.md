# 🛠️ Marketplace Examples

Welcome to the Marketplace Examples repository! This collection showcases practical implementations and usage examples for various marketplace applications and services.

## 📁 Available Examples

### 🔮 [Inait Forecasting Examples](./inait-predict-examples/)
Comprehensive examples for the Inait Forecasting platform - a powerful time series forecasting solution that makes advanced machine learning accessible for businesses of all sizes.

**What you'll find:**
- Client implementation examples
- Prediction scripts and workflows
- Data visualization and plotting utilities
- Interactive Jupyter notebooks for hands-on learning

**Perfect for:** Sales forecasting, demand planning, financial predictions, and any time-dependent business metrics.

---

## 🚀 Getting Started

Each example folder contains its own README with specific setup instructions and usage guidelines. Navigate to the application folder you're interested in to begin.

## 📋 Example Structure

Each application example follows a consistent structure:
- **Client Code**: Ready-to-use implementation examples
- **Documentation**: Detailed READMEs and guides
- **Interactive Examples**: Jupyter notebooks for exploration
- **Utilities**: Helper scripts and common functions

## 🔄 Coming Soon

This repository will continue to expand with examples for additional marketplace applications. Stay tuned for more powerful tools and integrations!

---

*Explore, learn, and build amazing solutions with marketplace applications.*

```mermaid
flowchart TD
    A([START HERE])
    A --> B{Q1: How large is your typical dataset for a single job?}
    B -->|Massive: > 1 GB| C[SaaS SOLUTION<br>Why: Architected for multi-GB data;<br>avoids upload timeouts.]
    B -->|Standard: < 1 GB| D{Q2: How do you want to handle billing and procurement?}
    D -->|Single Bill on Azure Invoice| E[SaaS SOLUTION<br>Why: Simplifies procurement and billing through Azure.]
    D -->|Direct Invoice from INAIT| F{Q3: What is your preference for infrastructure management?}
    F -->|Zero Maintenance| G[SaaS SOLUTION<br>Why: A fully managed service with no operational overhead.]
    F -->|Full Control in own Tenant| H[MANAGED APPLICATION<br>Why: For compliance, control,<br>or specific policy reasons.]