import LandingComponent, {
  type LandingPillar,
  type LandingStat,
  type LandingTestimonial,
} from "./LandingComponent";
import { LineChart, ShieldCheck, Sparkles } from "lucide-react";

const stats: LandingStat[] = [
  { label: "Teams scaled", value: "120+" },
  { label: "Workflows automated", value: "18k" },
  { label: "Avg. ROI in 6 months", value: "4.3x" },
];

const pillars: LandingPillar[] = [
  {
    icon: <Sparkles className="size-8 text-primary" />,
    title: "Mission-driven AI",
    description:
      "We build automation that keeps humans in the loop, empowering teams to focus on strategy instead of repetitive hand-offs.",
  },
  {
    icon: <ShieldCheck className="size-8 text-primary" />,
    title: "Enterprise trust",
    description:
      "SOC2-ready architecture, granular permissions, and full audit trails mean you can scale responsibly without security compromises.",
  },
  {
    icon: <LineChart className="size-8 text-primary" />,
    title: "Measurable outcomes",
    description:
      "Real-time insights and health dashboards help leaders prove impact and re-invest in the initiatives that move the needle.",
  },
];

const differentiators = [
  "Connect every system — from spreadsheets to CRMs — with a visual builder your operators will actually enjoy using.",
  "Launch AI copilots in hours, not months, thanks to reusable nodes and compliance-friendly guardrails.",
  "Co-create with our experts: we pair you with automation strategists who have scaled 7-figure ops teams.",
];

const testimonials: LandingTestimonial[] = [
  {
    quote:
      "We automated onboarding across HR, finance, and IT in three weeks. The platform pays for itself every quarter.",
    name: "Jared Cole",
    title: "COO, NovaLabs",
  },
  {
    quote:
      "Our revenue team finally has one place to orchestrate AI touchpoints. We 3x’d pipeline coverage with the same headcount.",
    name: "Amelia Nunez",
    title: "VP RevOps, StratusIQ",
  },
];

export default function LandingContainer() {
  return (
    <LandingComponent
      stats={stats}
      pillars={pillars}
      differentiators={differentiators}
      testimonials={testimonials}
    />
  );
}

