import type React from "react"
import type { Metadata } from "next"
import { ThemeProvider } from "@mui/material/styles"
import CssBaseline from "@mui/material/CssBaseline"
import { theme } from "./theme"
import "./globals.css"

export const metadata: Metadata = {
  title: "Neo4j Graph Visualization",
  description: "Interactive network graph powered by Neo4j and Next.js",
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        <ThemeProvider theme={theme}>
          <CssBaseline />
          {children}
        </ThemeProvider>
      </body>
    </html>
  )
}
