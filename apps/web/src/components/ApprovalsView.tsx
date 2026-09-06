import React, { useState } from 'react';
import { CheckCircle, XCircle, ShieldAlert, Lock, AlertTriangle, ArrowRight, Check, X, ShieldCheck } from 'lucide-react';
import { RemediationProposal, ApprovalStatus } from '../types';

interface ApprovalsViewProps {
  proposals: RemediationProposal[];
  onApprove: (proposalId: string, reason: string, idempotencyKey: string) => Promise<void>;
  onReject: (proposalId: string, reason: string, idempotencyKey: string) => Promise<void>;
  selectedProposal: RemediationProposal | null;
  onSelectProposal: (prop: RemediationProposal | null) => void;
}

export const ApprovalsView: React.FC<ApprovalsViewProps> = ({
  proposals,
  onApprove,
  onReject,
  selectedProposal,
  onSelectProposal,
}) => {
  const [modalAction, setModalAction] = useState<'approve' | 'reject' | null>(null);
  const [activeProp, setActiveProp] = useState<RemediationProposal | null>(selectedProposal);
  const [reason, setReason] = useState<string>('');
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleOpenModal = (prop: RemediationProposal, action: 'approve' | 'reject') => {
    setActiveProp(prop);
    setModalAction(action);
    setReason(action === 'approve' ? 'Authorized after operator sensor and runbook verification.' : 'Rejected due to field override.');
    setErrorMsg(null);
  };

  const handleConfirmAction = async () => {
    if (!activeProp || !modalAction) return;
    if (!reason.trim()) {
      setErrorMsg('A justification reason is strictly required by EdgeShield policy.');
      return;
    }

    setIsSubmitting(true);
    setErrorMsg(null);

    const idempotencyKey = `idem-ui-${activeProp.id}-${Date.now()}`;
    try {
      if (modalAction === 'approve') {
        await onApprove(activeProp.id, reason, idempotencyKey);
      } else {
        await onReject(activeProp.id, reason, idempotencyKey);
      }
      setModalAction(null);
      setActiveProp(null);
    } catch (err: any) {
      setErrorMsg(err.message || 'Action failed.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const pendingList = proposals.filter((p) => p.status === 'pending');
  const historyList = proposals.filter((p) => p.status !== 'pending');

  return (
    <div className="space-y-6">
      
      {/* Policy Banner */}
      <div className="p-4 rounded-xl border border-cyan-500/40 bg-cyan-950/20 text-cyan-300 flex items-start space-x-3">
        <div className="p-2 rounded-lg bg-cyan-900/40 shrink-0">
          <Lock className="w-5 h-5 text-cyan-400" />
        </div>
        <div>
          <h3 className="text-sm font-bold text-slate-100">Human-In-The-Loop (HITL) Policy Interlock</h3>
          <p className="text-xs text-slate-300 mt-0.5">
            Non-negotiable Rule #4: <strong>No disruptive action may execute without explicit human approval.</strong>
            Every remediation proposal requires a verified operator signature, unique idempotency token, and justification rationale.
          </p>
        </div>
      </div>

      {/* Pending Proposals Queue */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-bold uppercase tracking-wider text-slate-200 flex items-center space-x-2">
            <CheckCircle className="w-4 h-4 text-rose-400" />
            <span>Pending Remediation Proposals ({pendingList.length})</span>
          </h2>
        </div>

        {pendingList.length === 0 ? (
          <div className="cyber-card p-8 text-center text-slate-500 text-xs border-dashed">
            No remediation proposals awaiting approval.
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4">
            {pendingList.map((prop) => (
              <div
                key={prop.id}
                className="cyber-card p-5 border-amber-500/40 bg-gradient-to-r from-slate-900/90 to-amber-950/10 space-y-4"
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-3">
                  <div className="flex items-center space-x-2">
                    <span className="px-2.5 py-1 text-xs font-mono font-bold uppercase rounded bg-amber-500/20 text-amber-300 border border-amber-500/40">
                      {prop.action_type.replace(/_/g, ' ')}
                    </span>
                    <span className="text-xs font-mono text-slate-400">ID: {prop.id}</span>
                  </div>
                  <span className="text-[11px] font-mono text-rose-400">
                    Expires: {new Date(prop.expires_at).toLocaleTimeString()}
                  </span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                  <div className="space-y-2">
                    <p><strong className="text-slate-400">Target Device:</strong> <code className="text-cyan-300 font-bold">{prop.target_device_id}</code></p>
                    <p><strong className="text-slate-400">Scope:</strong> <code className="text-slate-200">{prop.scope}</code></p>
                    <p><strong className="text-slate-400">Justification:</strong> <span className="text-slate-200">{prop.reason}</span></p>
                  </div>
                  <div className="space-y-2">
                    <p><strong className="text-slate-400">Operational Impact:</strong> <span className="text-slate-300">{prop.impact_summary}</span></p>
                    <p><strong className="text-slate-400">Rollback Procedure:</strong> <span className="text-slate-300">{prop.rollback_procedure}</span></p>
                  </div>
                </div>

                {/* Approval Actions */}
                <div className="flex items-center justify-end space-x-3 pt-2">
                  <button
                    onClick={() => handleOpenModal(prop, 'reject')}
                    className="flex items-center space-x-1.5 px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-rose-400 text-xs font-semibold transition-all"
                  >
                    <X className="w-4 h-4" />
                    <span>Reject Proposal</span>
                  </button>
                  <button
                    onClick={() => handleOpenModal(prop, 'approve')}
                    className="flex items-center space-x-1.5 px-5 py-2 rounded-lg bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white text-xs font-bold shadow-lg shadow-emerald-950 transition-all glow-cyan"
                  >
                    <Check className="w-4 h-4" />
                    <span>Authorize Remediation</span>
                  </button>
                </div>

              </div>
            ))}
          </div>
        )}
      </div>

      {/* Historical Approvals */}
      {historyList.length > 0 && (
        <div className="space-y-3 pt-4">
          <h2 className="text-sm font-bold uppercase tracking-wider text-slate-400">
            Resolved Decision History ({historyList.length})
          </h2>
          <div className="space-y-2">
            {historyList.map((prop) => (
              <div key={prop.id} className="cyber-card p-3.5 text-xs flex flex-col sm:flex-row sm:items-center justify-between gap-2 opacity-80">
                <div className="flex items-center space-x-2">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase ${
                    prop.status === 'approved' ? 'bg-emerald-950 text-emerald-300 border border-emerald-800' : 'bg-rose-950 text-rose-300 border border-rose-800'
                  }`}>
                    {prop.status}
                  </span>
                  <span className="font-semibold text-slate-200">{prop.action_type} on {prop.target_device_id}</span>
                </div>
                <div className="text-[11px] text-slate-400 font-mono">
                  {prop.execution_result || 'Resolved'}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Confirmation Modal */}
      {modalAction && activeProp && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/85 backdrop-blur-sm">
          <div className="cyber-card p-6 max-w-lg w-full space-y-4 border-cyan-500/50 glow-cyan">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center space-x-2">
                <ShieldCheck className="w-5 h-5 text-cyan-400" />
                <h3 className="font-bold text-slate-100 text-sm">
                  {modalAction === 'approve' ? 'Confirm Remediation Authorization' : 'Confirm Proposal Rejection'}
                </h3>
              </div>
              <button onClick={() => setModalAction(null)} className="text-slate-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 space-y-1">
                <p><strong>Action:</strong> <span className="text-cyan-300 font-mono">{activeProp.action_type}</span></p>
                <p><strong>Target:</strong> <span className="text-slate-200 font-mono">{activeProp.target_device_id}</span></p>
                <p><strong>Scope:</strong> <span className="text-slate-400 font-mono">{activeProp.scope}</span></p>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Operator Justification Rationale (Mandatory for Audit Trail):
                </label>
                <textarea
                  value={reason}
                  onChange={(e) => setReason(e.target.value)}
                  rows={3}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2.5 text-xs text-slate-100 focus:outline-none focus:border-cyan-400 font-mono"
                  placeholder="Enter detailed reason for authorizing or rejecting..."
                />
              </div>

              {errorMsg && (
                <div className="p-2.5 rounded bg-rose-950/60 border border-rose-800 text-rose-300 text-xs">
                  {errorMsg}
                </div>
              )}
            </div>

            <div className="flex items-center justify-end space-x-2 pt-2">
              <button
                onClick={() => setModalAction(null)}
                disabled={isSubmitting}
                className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-300"
              >
                Cancel
              </button>
              <button
                onClick={handleConfirmAction}
                disabled={isSubmitting}
                className={`px-5 py-2 rounded-lg text-xs font-bold text-white transition-all ${
                  modalAction === 'approve'
                    ? 'bg-emerald-600 hover:bg-emerald-500 shadow-lg shadow-emerald-950'
                    : 'bg-rose-600 hover:bg-rose-500 shadow-lg shadow-rose-950'
                }`}
              >
                {isSubmitting ? 'Signing...' : modalAction === 'approve' ? 'Sign & Apply Action' : 'Confirm Rejection'}
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
};
