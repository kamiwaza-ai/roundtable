import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen p-8">
      <main className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold mb-8">Welcome to RoundTable</h1>
        
        <div className="grid gap-6 md:grid-cols-2">
          <Link 
            href="/agents"
            className="p-6 border rounded-lg hover:border-primary transition-colors"
          >
            <h2 className="text-2xl font-semibold mb-2">Agents</h2>
            <p className="text-muted-foreground">
              Create and manage AI agents with different roles and expertise
            </p>
          </Link>

          <Link 
            href="/round-tables"
            className="p-6 border rounded-lg hover:border-primary transition-colors"
          >
            <h2 className="text-2xl font-semibold mb-2">Round Tables</h2>
            <p className="text-muted-foreground">
              Start discussions between AI agents to solve problems and make decisions
            </p>
          </Link>
        </div>
      </main>
    </div>
  );
}
