import { useState, useEffect } from "react"
import { runEvaluation, listEvalReports } from "../api/eval"
import { PanelCard } from "../components/common/PanelCard"
import type { EvalReportItem } from "../types"
import { toast } from "sonner"

export function Eval() {
  const [reports, setReports] = useState<EvalReportItem[]>([])
  const [running, setRunning] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(
    function loadReportsOnMount() {
      listEvalReports()
        .then(function handleSuccess(response) {
          setReports(response.reports)
        })
        .catch(function handleError(err) {
          setError(err instanceof Error ? err.message : "Failed to load reports")
        })
    },
    [],
  )

  async function handleRun() {
    setRunning(true)
    setError(null)
    try {
      await runEvaluation()
      toast.success("[$ EVAL_COMPLETE] Report generated")
      const response = await listEvalReports()
      setReports(response.reports)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Evaluation failed")
      toast.error("[! EVAL_FAILED]")
    } finally {
      setRunning(false)
    }
  }

  return (
    <div className="animate-reveal-up">
      <div className="mb-6">
        <h1 className="font-body text-lg font-bold text-accent-primary tracking-wider uppercase mb-2">
          <span className="text-text-muted">// </span>EVALUATION
        </h1>
        <span className="font-body text-2xs text-text-ghost tracking-wider">
          RAGAS -- faithfulness, answer_relevancy, context_precision
        </span>
      </div>

      {error && (
        <div className="mb-4 px-4 py-2 bg-error/10 border border-error/20 rounded text-error text-xs font-body">
          [!] {error}
        </div>
      )}

      <PanelCard index="01" title="RUN_EVALUATION">
        <button
          onClick={handleRun}
          disabled={running}
          className="font-body text-sm font-medium tracking-wider uppercase px-6 py-3 bg-accent-primary text-bg-primary rounded-md hover:shadow-[0_0_20px_var(--color-accent-bg),0_0_60px_rgba(57,255,20,0.08)] transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {running ? (
            <span className="flex items-center gap-2">
              <span className="inline-block w-2 h-4 bg-bg-primary rounded-sm animate-cursor-blink" />
              RUNNING...
            </span>
          ) : (
            "$ EXECUTE_EVALUATION"
          )}
        </button>
      </PanelCard>

      <div className="mt-6">
        <PanelCard index="02" title="REPORTS">
          {reports.length === 0 ? (
            <p className="font-body text-sm text-text-muted">
              // NO_REPORTS -- run evaluation to generate
            </p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full border-collapse font-body text-sm">
                <thead>
                  <tr>
                    <th className="px-4 py-3 text-left text-text-muted text-xs font-medium tracking-widest uppercase border-b border-border-default">
                      NAME
                    </th>
                    <th className="px-4 py-3 text-right text-text-muted text-xs font-medium tracking-widest uppercase border-b border-border-default">
                      FAITHFULNESS
                    </th>
                    <th className="px-4 py-3 text-right text-text-muted text-xs font-medium tracking-widest uppercase border-b border-border-default">
                      RELEVANCY
                    </th>
                    <th className="px-4 py-3 text-right text-text-muted text-xs font-medium tracking-widest uppercase border-b border-border-default">
                      PRECISION
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {reports.map(function renderReport(report) {
                    return (
                      <tr
                        key={report.id}
                        className="border-b border-border-ghost hover:bg-bg-surface-hover"
                      >
                        <td className="px-4 py-3 text-text-primary">
                          {report.name}
                        </td>
                        <td className="px-4 py-3 text-right tabular-nums text-success">
                          {report.faithfulness != null
                            ? `${(report.faithfulness * 100).toFixed(1)}%`
                            : "—"}
                        </td>
                        <td className="px-4 py-3 text-right tabular-nums text-info">
                          {report.answer_relevancy != null
                            ? `${(report.answer_relevancy * 100).toFixed(1)}%`
                            : "—"}
                        </td>
                        <td className="px-4 py-3 text-right tabular-nums text-warning">
                          {report.context_precision != null
                            ? `${(report.context_precision * 100).toFixed(1)}%`
                            : "—"}
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          )}
        </PanelCard>
      </div>
    </div>
  )
}
