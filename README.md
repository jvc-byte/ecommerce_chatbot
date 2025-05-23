# Electronics E-commerce Store

A full-stack e-commerce application for selling electronics built with React and Python.

## Features
- Browse electronics products
- Product details view
- Shopping cart functionality
- Modern and responsive UI
- Real-time product search and recommendations
- Product categorization and filtering

## Technologies Used

| Category | Technology | Purpose |
|----------|------------|---------|
| Frontend Framework | React.js | Modern JavaScript library for building user interfaces |
| Frontend Routing | React Router | Client-side routing |
| HTTP Client | Axios | Making HTTP requests to backend |
| UI Components | Material-UI | Modern and responsive UI components |
| State Management | LocalStorage | Cart persistence |
| CSS Styling | CSS Modules | Component-specific styling |
| Frontend Build | Webpack | Module bundling and asset management |
| Frontend Development | Babel | JavaScript compiler for modern JS features |
| Frontend Testing | Jest | JavaScript testing framework |
| Frontend Linting | ESLint | Code quality and style checking |
|---------|---------|---------|
| Backend Framework | Flask | Python web framework |
| Backend CORS | Flask-CORS | Cross-origin resource sharing |
| Data Storage | JSON Files | Product catalog storage |
| API Development | RESTful | Backend API architecture |
| Development Environment | Virtualenv | Python virtual environment |
| Package Management | pip | Python package management |
| Backend Testing | pytest | Python testing framework |
|---------|---------|---------|
| Chatbot Core | Python | Chatbot service implementation |
| LLM Provider | Google Gemini | Preferred AI model |
| LLM Provider | OpenAI | Alternative AI model |
| LLM Provider | HuggingFace | Alternative AI model |
| LLM Provider | Local LLM | Alternative AI model (e.g., Ollama) |
| Natural Language Processing | Custom Implementation | Product search and recommendation |
| Chat State | Conversation History | Context-aware responses |
| API Integration | REST | Chatbot API endpoints |
| Error Handling | Custom Implementation | Robust error management |
|---------|---------|---------|
| Development Tools | VS Code | Code editing and development |
| Version Control | Git | Source code versioning |
| Package Management | npm | Frontend package management |
| Development Environment | Node.js | JavaScript runtime |
| Build Tools | npm scripts | Project build and deployment |
| Debugging | Chrome DevTools | Frontend debugging |
|---------|---------|---------|
| Deployment | Local Development | Development environment |

Note: The project is designed to be lightweight and easy to set up, using JSON files for data storage instead of a traditional database system.

## Project Structure

```
ecommerce/
├── backend/           # Flask backend server
│   ├── app.py        # Main application with REST API
│   └── requirements.txt
│
├── frontend/          # React frontend application
│   ├── public/       # Static files
│   └── src/          # Source code
│       ├── components/ # Reusable React components
│       └── pages/    # Page components
│
├── chatbot/          # AI chatbot service
│   ├── chatbot_service.py # Main chatbot implementation
│   └── requirements.txt
│
└── database/         # Data storage
    └── products.json # Product catalog
```

## Setup Instructions

### Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup

1. Create and activate virtual environment:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Start the backend server:
```bash
python app.py
```
The backend will run on http://localhost:5000

### Chatbot Setup

1. Set up environment variables:
```bash
cd chatbot
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Start the chatbot service:
```bash
python chatbot_service.py
```
The chatbot will run on http://localhost:5001

### Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Start the development server:
```bash
npm start
```
The frontend will run on http://localhost:3000

### Running the Application

1. In separate terminals:
```bash
# Terminal 1 - Backend
python backend/app.py

# Terminal 2 - Chatbot
python chatbot/chatbot_service.py

# Terminal 3 - Frontend
npm start
```

The application will be available at http://localhost:3000

## API Documentation

### Backend API

- GET `/api/products` - Get all products
- GET `/api/product/:id` - Get a specific product
- POST `/api/cart` - Add item to cart
  - Body: { "product_id": number, "quantity": number }

### Chatbot API

- POST `/api/chat` - Send message to chatbot
  - Body: { "message": string, "session_id": string }
- DELETE `/api/chat/clear` - Clear conversation history
- GET `/api/products` - Get all products (for debugging)
- GET `/api/health` - Health check endpoint

## Product Data Structure

```json
{
    "id": number,
    "name": string,
    "price": number,
    "description": string,
    "category": string,
    "image": string,
    "stock": number
}
```

## Development Notes

- The application uses JSON files for data storage, making it lightweight and easy to set up
- The chatbot service is modular and can be configured to use different LLM providers
- Frontend uses localStorage for cart persistence
- All API endpoints are CORS-enabled for cross-origin requests

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
