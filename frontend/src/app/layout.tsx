import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";
import { AppProvider } from "@/context/AppContext";

export const metadata: Metadata = {
  title: "GourmetAI - Engineering Taste through Data",
  description: "Premium Zomato Bangalore Restaurant Recommendation Engine",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <AppProvider>
          {/* Global Header */}
          <header className="header-container">
            <Link href="/" className="logo">
              <span>🥘</span> GourmetAI
            </Link>
            <nav className="nav-links">
              <Link href="/" className="nav-link">Home</Link>
              <Link href="/preferences" className="nav-link">Discover</Link>
            </nav>
            <div className="header-right">
              <button className="search-icon-btn">🔍</button>
              <img 
                src="https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&q=80&w=100" 
                alt="User Profile" 
                className="user-avatar"
              />
            </div>
          </header>

          {/* Children views */}
          {children}

          {/* Global Footer */}
          <footer className="footer-credits">
            <p>© 2024 GourmetAI. Engineering taste through data.</p>
          </footer>
        </AppProvider>
      </body>
    </html>
  );
}
