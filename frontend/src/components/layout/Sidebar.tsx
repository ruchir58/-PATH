"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, UploadCloud, Users, BarChart3, Settings } from "lucide-react";
import clsx from "clsx";

const navItems = [
  { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { name: "Upload Data", href: "/upload", icon: UploadCloud },
  { name: "Students", href: "/students", icon: Users },
  { name: "Class Analytics", href: "/analytics", icon: BarChart3 },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 bg-[#E5D9C5] text-[#4A3B32] flex flex-col shadow-lg h-full">
      <div className="p-6">
        <h1 className="text-2xl font-bold tracking-wider">प्रगति-PATH</h1>
        <p className="text-sm mt-2 opacity-80">Early Warning System</p>
      </div>

      <nav className="flex-1 mt-6 space-y-2 px-4">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname.startsWith(item.href);
          return (
            <Link
              key={item.name}
              href={item.href}
              className={clsx(
                "flex items-center space-x-3 px-4 py-3 rounded-xl transition-colors duration-200",
                isActive
                  ? "bg-[#4A3B32] text-[#E5D9C5] shadow-md"
                  : "hover:bg-[#D5C6AF] hover:text-[#4A3B32]"
              )}
            >
              <Icon size={20} />
              <span className="font-medium">{item.name}</span>
            </Link>
          );
        })}
      </nav>

      <div className="p-4 border-t border-[#D5C6AF]">
        <button className="flex items-center space-x-3 px-4 py-3 rounded-xl w-full hover:bg-[#D5C6AF] hover:text-[#4A3B32] transition-colors duration-200">
          <Settings size={20} />
          <span className="font-medium">Settings</span>
        </button>
      </div>
    </aside>
  );
}
