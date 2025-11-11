import { Button } from "@/components/ui/button";
import { ArrowRight, Rocket, Sparkles } from "lucide-react";
import type { ReactNode } from "react";
import { Link } from "react-router-dom";

export interface LandingStat {
  label: string;
  value: string;
}

export interface LandingPillar {
  icon: ReactNode;
  title: string;
  description: string;
}

export interface LandingTestimonial {
  quote: string;
  name: string;
  title: string;
}

interface LandingComponentProps {
  stats: LandingStat[];
  pillars: LandingPillar[];
  differentiators: string[];
  testimonials: LandingTestimonial[];
}

export default function LandingComponent({
  stats,
  pillars,
  differentiators,
  testimonials,
}: LandingComponentProps) {
  return (
    <div className="min-h-screen bg-gradient-to-b from-background via-background to-secondary/40 text-foreground">
      <header className="relative overflow-hidden bg-primary/5">
        <div className="absolute inset-0 -z-10">
          <div className="absolute -left-32 top-32 hidden size-[380px] rounded-full bg-primary/15 blur-3xl mix-blend-multiply sm:block" />
          <div className="absolute -right-16 top-0 hidden size-[280px] rounded-full bg-secondary/40 blur-3xl mix-blend-multiply sm:block" />
        </div>
        <div className="mx-auto flex max-w-6xl flex-col gap-16 px-6 py-16 sm:px-12 sm:py-24 lg:px-16">
          <div className="flex flex-col gap-12 lg:flex-row lg:items-center lg:justify-between">
            <div className="max-w-2xl space-y-6 text-center lg:text-left">
              <span className="mx-auto inline-flex items-center gap-2 rounded-full bg-primary/10 px-4 py-1 text-sm font-semibold text-primary lg:mx-0">
                <Sparkles className="size-4" />
                Intelligent operations, human-first outcomes
              </span>
              <h1 className="text-balance text-4xl font-semibold tracking-tight sm:text-5xl">
                Automate customer journeys without sacrificing authenticity.
              </h1>
              <p className="text-pretty text-lg text-muted-foreground">
                Our mission is to make advanced automation accessible to every growth team. We bring your data,
                playbooks, and AI copilots into one orchestrated platform—so you ship resilient customer experiences and
                reclaim your team’s creative energy.
              </p>
              <div className="flex flex-wrap items-center justify-center gap-4 lg:justify-start">
                <Button asChild size="lg">
                  <Link to="/register">
                    Start Free Trial
                    <ArrowRight className="size-4" />
                  </Link>
                </Button>
                <Button asChild size="lg" variant="outline">
                  <Link to="/login">Talk to Sales</Link>
                </Button>
              </div>
            </div>

            <div className="relative mx-auto max-w-lg rounded-3xl border border-primary/20 bg-background/70 p-6 shadow-xl shadow-primary/10 backdrop-blur sm:p-8">
              <div className="absolute -top-20 right-6 hidden w-32 rounded-2xl border border-primary/20 bg-primary/10 p-4 text-xs font-semibold uppercase tracking-wide text-primary backdrop-blur sm:block">
                Workflow health
                <div className="mt-3 text-lg font-bold text-foreground">98.6%</div>
                <p className="mt-1 text-xs text-muted-foreground">+12% in the last 30 days</p>
              </div>
              <div className="space-y-6">
                <div>
                  <p className="text-xs font-semibold uppercase text-primary/70">Velocity</p>
                  <div className="mt-2 flex items-end gap-1 text-4xl font-semibold">
                    42
                    <span className="text-sm font-medium text-muted-foreground">routines</span>
                  </div>
                  <p className="mt-2 text-sm text-muted-foreground">
                    Seamlessly orchestrate LLM agents, triggers, and approvals in minutes.
                  </p>
                </div>
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
                  {stats.map((stat) => (
                    <div
                      key={stat.label}
                      className="rounded-2xl border border-border bg-background/80 p-4 text-center shadow-sm"
                    >
                      <div className="text-xl font-semibold text-foreground">{stat.value}</div>
                      <div className="mt-1 text-xs font-medium uppercase text-muted-foreground">{stat.label}</div>
                    </div>
                  ))}
                </div>
              </div>
              <div className="absolute -bottom-10 left-6 hidden w-40 flex-col gap-2 rounded-2xl border border-border bg-background/90 p-4 text-sm shadow-lg sm:flex">
                <div className="flex items-center gap-2 font-semibold">
                  <Rocket className="size-4 text-primary" />
                  Launch success
                </div>
                <p className="text-xs text-muted-foreground">
                  Shipping new journeys in under 14 days with our launch playbooks.
                </p>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="mx-auto flex max-w-6xl flex-col gap-24 px-6 py-16 sm:px-12 lg:px-16">
        <section className="grid gap-12 lg:grid-cols-[1.1fr_0.9fr] lg:items-center">
          <div className="space-y-6">
            <h2 className="text-balance text-3xl font-semibold tracking-tight sm:text-4xl">Why we exist</h2>
            <p className="text-pretty text-lg text-muted-foreground">
              Growth teams are drowning in brittle tooling, siloed data, and manual updates. We believe automation should
              augment the humans behind your brand—not replace them. Our platform unifies AI, human approvals, and live
              data so every customer touchpoint feels timely, contextual, and authentic.
            </p>
            <div className="space-y-4">
              {differentiators.map((item) => (
                <div key={item} className="flex gap-3">
                  <div className="mt-1 size-2 rounded-full bg-primary" />
                  <p className="text-pretty text-base text-foreground/90">{item}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="grid gap-6 rounded-3xl bg-primary/5 p-6 backdrop-blur sm:p-10">
            {pillars.map((pillar) => (
              <div key={pillar.title} className="flex flex-col gap-4 rounded-2xl border border-border/60 bg-background/80 p-6 sm:flex-row sm:gap-5">
                <div className="flex size-12 items-center justify-center rounded-full bg-primary/10">
                  {pillar.icon}
                </div>
                <div>
                  <h3 className="text-lg font-semibold">{pillar.title}</h3>
                  <p className="mt-2 text-sm text-muted-foreground">{pillar.description}</p>
                </div>
              </div>
            ))}
          </div>
        </section>

        <section className="rounded-3xl border border-border bg-background/80 p-8 shadow-lg shadow-primary/5 sm:p-12">
          <div className="flex flex-col gap-8 lg:flex-row lg:items-center lg:justify-between">
            <div className="max-w-xl space-y-4 text-center lg:text-left">
              <h2 className="text-balance text-3xl font-semibold tracking-tight sm:text-4xl">
                Build trustworthy AI-led journeys end to end.
              </h2>
              <p className="text-pretty text-base text-muted-foreground">
                Activate plug-and-play workflow templates, sync customer context from every system, and deploy guardrails
                that keep your brand voice consistent—even as you scale.
              </p>
            </div>
            <div className="flex flex-wrap items-center justify-center gap-6 lg:justify-end">
              {stats.map((stat) => (
                <div key={stat.label} className="text-center">
                  <p className="text-3xl font-semibold text-primary">{stat.value}</p>
                  <p className="text-xs font-medium uppercase text-muted-foreground">{stat.label}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="grid gap-10 lg:grid-cols-2">
          {testimonials.map((testimonial) => (
            <blockquote
              key={testimonial.name}
              className="flex flex-col gap-4 rounded-3xl border border-border bg-background/80 p-8 shadow-sm"
            >
              <p className="text-pretty text-lg italic text-foreground/90">&ldquo;{testimonial.quote}&rdquo;</p>
              <div className="text-sm font-medium text-primary">
                {testimonial.name}
                <span className="ml-2 text-muted-foreground">· {testimonial.title}</span>
              </div>
            </blockquote>
          ))}
        </section>
      </main>

      <footer className="bg-foreground text-background">
        <div className="mx-auto flex max-w-6xl flex-col gap-8 px-6 py-16 text-center sm:px-12 sm:py-20">
          <div className="flex flex-wrap items-center justify-center gap-2 text-sm font-semibold uppercase tracking-[0.3em]">
            <Sparkles className="size-4" />
            Ready to orchestrate?
          </div>
          <h2 className="mx-auto max-w-2xl text-balance text-3xl font-semibold sm:text-4xl">
            Launch your next intelligent journey with us in under two weeks.
          </h2>
          <p className="mx-auto max-w-xl text-pretty text-base text-muted-background">
            Every plan starts with collaborative strategy sessions and a purpose-built roadmap tailored to your revenue
            goals.
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <Button asChild size="lg" variant="secondary" className="text-primary">
              <Link to="/register">
                Get Started Now
                <ArrowRight className="size-4" />
              </Link>
            </Button>
            <Button
              asChild
              size="lg"
              variant="outline"
              className="border-background text-background hover:bg-background/10"
            >
              <Link to="/login">View Platform Demo</Link>
            </Button>
          </div>
        </div>
      </footer>
    </div>
  );
}

