export default function Section({ title, children }) {
  return (
    <section className="card">
      <header>
        <h2>{title}</h2>
      </header>
      <div>{children}</div>
    </section>
  );
}
