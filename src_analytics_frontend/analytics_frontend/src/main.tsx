import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider } from "@material-tailwind/react";
import { ApolloClient, InMemoryCache, ApolloProvider } from "@apollo/client";
// local
import './index.css'
import App from './App.tsx'

const client = new ApolloClient({
  uri: "http://localhost:8001/graphql", // Replace with your GraphQL server URL
  cache: new InMemoryCache(),
});

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ThemeProvider>
      <BrowserRouter>
        <ApolloProvider client={client}>
          <App />
        </ApolloProvider>
      </BrowserRouter>
    </ThemeProvider>
  </StrictMode>,
)
