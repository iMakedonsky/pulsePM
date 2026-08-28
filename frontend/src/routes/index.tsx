import { createFileRoute } from '@tanstack/react-router';

export const Route = createFileRoute('/')({ component: Home });

function Home() {
  return (
    <main className="page-wrap py-16">
      <section className="island-shell rise-in rounded-3xl p-8 md:p-14">
        <p className="island-kicker">Project workspace</p>
        <h1 className="display-title mt-3 text-5xl font-bold">
          Bring every project into focus.
        </h1>
        <p className="mt-5 max-w-2xl text-lg text-[var(--sea-ink-soft)]">
          PulsePM keeps teams aligned on the work that matters. Sign in from the
          top bar to view your protected profile.
        </p>
      </section>
    </main>
  );
}
