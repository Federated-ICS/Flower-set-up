# OSB Watchtower 🛡️

A modern cybersecurity monitoring and threat intelligence dashboard built with Next.js, featuring real-time alert management, federated learning status tracking, and interactive MITRE ATT&CK technique visualization.

![Next.js](https://img.shields.io/badge/Next.js-16.0-black?style=flat-square&logo=next.js)
![React](https://img.shields.io/badge/React-19.2-blue?style=flat-square&logo=react)
![TypeScript](https://img.shields.io/badge/TypeScript-5.x-blue?style=flat-square&logo=typescript)
![Tailwind CSS](https://img.shields.io/badge/Tailwind-4.1-38bdf8?style=flat-square&logo=tailwind-css)
![CI](https://github.com/Federated-ICS/webapp/workflows/Frontend%20CI%20Pipeline/badge.svg)

## ✨ Features

### 🎯 Dashboard
- **System Status Overview**: Real-time monitoring of active alerts, FL progress, and prediction accuracy
- **Recent Alerts Feed**: Quick view of the latest security incidents
- **Attack Prediction**: ML-powered predictions of potential attack techniques
- **Quick Actions**: Fast access to common security operations

### 🚨 Alert Management
- **Advanced Filtering**: Filter by severity (critical, high, medium, low), facility, and time range
- **Search Functionality**: Full-text search across alert titles and descriptions
- **Alert Statistics**: Track total alerts, critical incidents, unresolved cases, and false positives
- **Multiple Detection Sources**: LSTM Model, Isolation Forest, Physics Model, and System Monitor
- **Pagination**: Efficient browsing through large alert datasets

### 🤝 Federated Learning Status
- **Round Progress Tracking**: Monitor current FL training rounds in real-time
- **Client Status**: Track 6 facility clients with individual progress, loss, and accuracy metrics
- **Privacy Metrics**: Display epsilon, delta, data size, and encryption standards
- **Round History**: Historical view of completed training rounds with accuracy trends

### 🕸️ Attack Graph Visualization
- **Interactive D3.js Graph**: Force-directed graph showing attack technique relationships
- **MITRE ATT&CK Integration**: Visualize current and predicted attack techniques
- **Technique Details**: Comprehensive information including:
  - Description and tactics
  - Detection strategies
  - Mitigation recommendations
  - Affected platforms
- **Attack Timeline**: Temporal view of attack progression
- **Zoom & Pan**: Interactive navigation of complex attack chains

## 🚀 Getting Started

### Prerequisites

- **Node.js** 22.x or higher
- **pnpm** 10.x (recommended) or npm

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Federated-ICS/webapp.git
   cd webapp
   ```

2. **Install dependencies**
   ```bash
   pnpm install
   # or
   npm install
   ```

3. **Run the development server**
   ```bash
   pnpm dev
   # or
   npm run dev
   ```

4. **Open your browser**
   
   Navigate to [http://localhost:3000](http://localhost:3000)

### Build for Production

```bash
pnpm build
pnpm start
```

## 📁 Project Structure

```
cybersentry-watchtower/
├── app/                      # Next.js App Router
│   ├── alerts/              # Alert management page
│   ├── attack-graph/        # Attack visualization page
│   ├── fl-status/           # Federated learning page
│   ├── layout.tsx           # Root layout
│   ├── page.tsx             # Dashboard home
│   └── globals.css          # Global styles
├── components/              # React components
│   ├── ui/                  # Reusable UI components (Radix UI)
│   ├── header.tsx           # Navigation header
│   ├── footer.tsx           # Footer
│   ├── alert-table.tsx      # Alert table component
│   ├── force-directed-graph.tsx  # D3.js graph
│   └── ...                  # Other feature components
├── utils/                   # Utility functions
│   ├── mock-data.ts         # Mock alert and FL data
│   ├── attack-graph-data.ts # MITRE ATT&CK data
│   └── format-time.ts       # Time formatting utilities
├── lib/                     # Shared libraries
│   └── utils.ts             # Helper functions
├── hooks/                   # Custom React hooks
├── public/                  # Static assets
└── styles/                  # Additional styles
```

## 🛠️ Tech Stack

- **Framework**: [Next.js 16](https://nextjs.org/) with App Router
- **UI Library**: [React 19](https://react.dev/)
- **Language**: [TypeScript](https://www.typescriptlang.org/)
- **Styling**: [Tailwind CSS 4](https://tailwindcss.com/)
- **UI Components**: [Radix UI](https://www.radix-ui.com/)
- **Data Visualization**: [D3.js](https://d3js.org/)
- **Charts**: [Recharts](https://recharts.org/)
- **Icons**: [Lucide React](https://lucide.dev/)
- **Background Effects**: [Vanta.js](https://www.vantajs.com/)
- **Form Handling**: [React Hook Form](https://react-hook-form.com/) + [Zod](https://zod.dev/)

## 📊 Data Sources

The application connects to a backend API for real-time data:

- **Alerts**: Security alerts from multiple detection layers (LSTM, Isolation Forest, Physics Model, System Monitor)
- **FL Clients**: Federated learning client status and training metrics
- **Attack Techniques**: MITRE ATT&CK techniques and predictions
- **Privacy Metrics**: Differential privacy parameters (epsilon, delta)

### Backend Configuration

Set the backend API URL in your environment:

```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
```

The API client is located in `lib/api-client.ts` and handles all backend communication.

## 🎨 Customization

### Theme

The application uses a dark cybersecurity theme. Customize colors in:
- `app/globals.css` - CSS variables
- `tailwind.config.js` - Tailwind configuration (if created)

### Components

All components are modular and can be customized independently. Key components:
- `components/header.tsx` - Navigation and branding
- `components/card.tsx` - Card wrapper with glow effects
- `components/ui/*` - Base UI components from Radix UI

## 🔒 Security Considerations

- **Environment Variables**: Never commit `.env` files with secrets
- **API Keys**: Store sensitive keys in environment variables
- **CORS**: Configure CORS properly when connecting to backend APIs
- **Authentication**: Implement authentication before deploying to production
- **Input Validation**: Validate all user inputs on both client and server

## 📝 Available Scripts

- `pnpm dev` - Start development server (port 3000)
- `pnpm build` - Build for production
- `pnpm start` - Run production build
- `pnpm lint` - Run ESLint for code quality
- `pnpm test` - Run tests with Vitest
- `pnpm test:ui` - Run tests with UI
- `pnpm test:coverage` - Run tests with coverage report
- `pnpm type-check` - Run TypeScript type checking

## 🔄 CI/CD Pipeline

The project includes a GitHub Actions CI pipeline that runs on every push and pull request:

- **Linting**: ESLint code quality checks
- **Testing**: Vitest unit and integration tests with coverage
- **Type Checking**: TypeScript compilation (currently disabled, pending fixes)
- **Building**: Next.js production build verification
- **Coverage**: Automatic upload to Codecov

See `.github/workflows/ci.yml` for the complete pipeline configuration.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- MITRE ATT&CK® framework for attack technique taxonomy
- Radix UI for accessible component primitives
- D3.js community for visualization examples
- Vanta.js for animated backgrounds

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Built with ❤️ for cybersecurity professionals**
