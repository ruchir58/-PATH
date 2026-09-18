import type { Metadata } from "next";
import { Inter, Geist } from "next/font/google";
import "./globals.css";
import Sidebar from "@/components/layout/Sidebar";
import { cn } from "@/lib/utils";

const geist = Geist({subsets:['latin'],variable:'--font-sans'});

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "प्रगति-PATH | Student Risk Warning System",
  description: "Academic Risk Early Warning System for Students",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={cn("font-sans", geist.variable)}>
      <body className={`${inter.className} bg-[#F5F5DC] text-[#4A3B32]`}>
        <div className="flex h-screen overflow-hidden">
          <Sidebar />
          <div className="flex-1 flex flex-col">
            <main className="flex-1 overflow-y-auto p-6">
              {children}
            </main>
          </div>
        </div>
      </body>
    </html>
  );
}
