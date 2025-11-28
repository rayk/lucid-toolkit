#!/usr/bin/env python3
"""
Command-line interface for session reconciliation.

Analyzes all active sessions, detects stale/ended sessions, backfills statistics
from transcripts, and updates sessions_summary.json.

Usage:
    python3 reconcile_cli.py [--dry-run] [--verbose]
"""
import sys
import argparse
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from session_summary.lib.reconciliator import SessionReconciliator
from session_summary.lib.session_manager import SessionManager


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Reconcile session tracking data from transcripts and logs"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without modifying files"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Aggressive cleanup: move all sessions older than 2 hours to history"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed information"
    )
    args = parser.parse_args()

    print("🔍 Session Reconciliation Starting...")
    print()

    # Load current state
    manager = SessionManager()
    data = manager.load()

    active_count_before = len(data.get("activeSessions", []))
    history_count_before = len(data.get("recentHistory", []))

    print(f"📊 Current State:")
    print(f"   Active sessions: {active_count_before}")
    print(f"   Recent history: {history_count_before}")
    print()

    if args.dry_run:
        print("⚠️  DRY RUN MODE - No changes will be saved")
        print()

    if args.strict:
        print("⚡ STRICT MODE - Aggressive cleanup enabled (2h threshold)")
        print()

    # Run reconciliation
    try:
        reconciliator = SessionReconciliator()

        # Apply strict mode if requested
        if args.strict:
            reconciliator.detector.ACTIVE_THRESHOLD_HOURS = 2
            reconciliator.detector.ZOMBIE_THRESHOLD_HOURS = 2

        if args.verbose:
            print("🔄 Analyzing sessions...")
            for session in data.get("activeSessions", []):
                print(f"   • {session['sessionId']}: {session['environment']['transcriptPath']}")
            print()

        report = reconciliator.reconcile_all_sessions()

        # If dry-run, don't save
        if args.dry_run:
            print("⚠️  Dry run complete - no changes were saved")
            return

        # Show results
        print("✅ Reconciliation Complete!")
        print()
        print(f"📋 Actions Taken:")
        print(f"   ✓ Moved to history: {report.moved_count} sessions")
        if report.moved_to_history:
            for session_id in report.moved_to_history:
                print(f"     - {session_id}")

        print(f"   ✓ Cleaned test sessions: {report.cleaned_count}")
        if report.cleaned_test_sessions:
            for session_id in report.cleaned_test_sessions:
                print(f"     - {session_id}")

        print(f"   ✓ Backfilled statistics: {report.backfilled_count}")
        if args.verbose and report.backfilled_stats:
            for session_id in report.backfilled_stats:
                print(f"     - {session_id}")

        print(f"   ✓ Preserved active: {report.active_count}")
        if args.verbose and report.preserved_active:
            for session_id in report.preserved_active:
                print(f"     - {session_id}")

        if report.errors:
            print(f"   ⚠️  Errors encountered: {len(report.errors)}")
            for error in report.errors:
                print(f"     - {error}")

        print()

        # Load final state
        final_data = manager.load()
        active_count_after = len(final_data.get("activeSessions", []))
        history_count_after = len(final_data.get("recentHistory", []))

        print(f"📊 Final State:")
        print(f"   Active sessions: {active_count_after} (was {active_count_before})")
        print(f"   Recent history: {history_count_after} (was {history_count_before})")
        print()
        print("✨ Session tracking data is now up to date!")

    except Exception as e:
        print(f"❌ Error during reconciliation: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
