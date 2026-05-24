import { apiRequest } from "../lib/api"
import type { EvalRunResponse, EvalReportsResponse } from "../types"

export function runEvaluation(name: string = "auto_eval", datasetPath?: string) {
  return apiRequest<EvalRunResponse>("/eval/run", {
    method: "POST",
    body: { name, dataset_path: datasetPath || null },
  })
}

export function listEvalReports() {
  return apiRequest<EvalReportsResponse>("/eval/reports")
}
