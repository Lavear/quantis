import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { api } from "./lib/api";
import Auth from "./pages/Auth";
import Onboard from "./pages/Onboard";
import Dashboard from "./pages/Dashboard";
import "./index.css";

const qc = new QueryClient();
const Guard = ({ children }: { children: React.ReactNode }) =>
  api.isAuthed() ? <>{children}</> : <Navigate to="/auth" />;

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <QueryClientProvider client={qc}>
      <BrowserRouter>
        <Routes>
          <Route path="/auth" element={<Auth />} />
          <Route path="/onboard" element={<Guard><Onboard /></Guard>} />
          <Route path="/" element={<Guard><Dashboard /></Guard>} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  </React.StrictMode>
);
