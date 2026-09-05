import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { api } from "../lib/api";
import { useCase } from "../lib/CaseContext";
import { StepFooter } from "../components/AppShell";
import ErrorBanner from "../components/ErrorBanner";

export default function HumanWitness() {
  const navigate = useNavigate();
  const { incidentId } = useCase();
  const [question, setQuestion] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [confirmation, setConfirmation] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const loadNext = () => {
    setLoading(true);
    setError(null);
    api.getNextQuestion(incidentId).then((q) => {
      setQuestion(q.question_id ? q : null);
      setLoading(false);
    }).catch((e) => {
      setError(String(e.message || e));
      setLoading(false);
    });
  };

  useEffect(loadNext, [incidentId]);

  const answer = async (value: "YES" | "NO" | "NOT_SURE") => {
    if (!question || submitting) return;
    setSubmitting(true);
    setError(null);
    try {
      const res = await api.postAttestation(incidentId, { question_id: question.question_id, answer: value });
      setConfirmation(res.message);
      setTimeout(() => {
        setConfirmation(null);
        setSubmitting(false);
        loadNext();
      }, 1400);
    } catch (e: any) {
      setError(String(e.message || e));
      setSubmitting(false);
    }
  };

  return (
    <div className="max-w-canvas mx-auto px-6 sm:px-10 py-16">
      <p className="label-eyebrow mb-4">Step 5 &middot; Human Witness</p>
      <h1 className="font-display text-[32px] sm:text-[36px] leading-tight mb-4">
        One thing only you can tell us.
      </h1>
      <p className="text-[15px] leading-relaxed text-forest/70 mb-14 max-w-[520px]">
        We ask one question at a time, starting with the one that changes the case the most.
      </p>

      <div className="max-w-[600px]">
        {error && <ErrorBanner message={error} onRetry={loadNext} />}
        <AnimatePresence mode="wait">
          {error ? null : confirmation ? (
            <motion.div
              key="confirmation"
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
              className="paper-card px-8 py-10 text-center"
            >
              <p className="text-[15px] font-ui text-forest/80">{confirmation}</p>
            </motion.div>
          ) : loading ? (
            <p className="text-forest/40 text-[14px]">Finding the next question&hellip;</p>
          ) : question ? (
            <motion.div
              key={question.question_id}
              initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
              className="paper-card px-8 py-10"
            >
              <p className="font-display text-[24px] sm:text-[28px] leading-snug mb-9">
                {question.question_text}
              </p>
              <div className="flex flex-col sm:flex-row gap-3">
                <button disabled={submitting} className="btn-witness border-emerald text-emerald hover:bg-emerald/10 disabled:opacity-40" onClick={() => answer("YES")}>
                  Yes
                </button>
                <button disabled={submitting} className="btn-witness border-vermillion text-vermillion hover:bg-vermillion/10 disabled:opacity-40" onClick={() => answer("NO")}>
                  No
                </button>
                <button disabled={submitting} className="btn-witness border-amber text-amber hover:bg-amber/10 disabled:opacity-40" onClick={() => answer("NOT_SURE")}>
                  I&rsquo;m not sure
                </button>
              </div>
            </motion.div>
          ) : (
            <div className="paper-card px-8 py-10">
              <p className="text-[15px] font-ui text-forest/70 mb-6">
                That&rsquo;s everything we needed from you directly. The rest is in your records and
                the evidence you shared.
              </p>
              <button className="btn-primary" onClick={() => navigate("/exposure")}>
                See the exposure
              </button>
            </div>
          )}
        </AnimatePresence>
      </div>

      <StepFooter current="/witness" />
    </div>
  );
}
