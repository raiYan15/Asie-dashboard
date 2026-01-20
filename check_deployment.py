#!/usr/bin/env python3
"""
ASIE Deployment Health Check
Validates that all required files are present before deployment
"""
import sys
from pathlib import Path

def check_deployment_readiness():
    """Check if project is ready for deployment"""
    
    ROOT = Path(__file__).parent
    issues = []
    warnings = []
    
    print("🔍 ASIE Deployment Health Check\n")
    print("=" * 50)
    
    # 1. Check critical files
    print("\n✓ Checking critical files...")
    critical_files = [
        "api/main.py",
        "requirements.txt",
        "Procfile",
        "runtime.txt",
        ".gitignore",
        "dashboard/package.json",
        "dashboard/index.html",
        "dashboard/vite.config.js",
    ]
    
    for file in critical_files:
        path = ROOT / file
        if not path.exists():
            issues.append(f"Missing critical file: {file}")
        else:
            print(f"  ✓ {file}")
    
    # 2. Check processed data
    print("\n✓ Checking processed data files...")
    data_dir = ROOT / "data" / "processed"
    if not data_dir.exists():
        issues.append("Missing data/processed directory")
    else:
        parquet_files = list(data_dir.glob("*.parquet"))
        print(f"  ✓ Found {len(parquet_files)} parquet files")
        if len(parquet_files) < 10:
            warnings.append(f"Only {len(parquet_files)} parquet files found (expected 17)")
    
    # 3. Check frontend dependencies
    print("\n✓ Checking frontend setup...")
    pkg_json = ROOT / "dashboard" / "package.json"
    if pkg_json.exists():
        print("  ✓ package.json exists")
        node_modules = ROOT / "dashboard" / "node_modules"
        if not node_modules.exists():
            warnings.append("node_modules not found - run 'npm install' in dashboard/")
    
    # 4. Check git repository
    print("\n✓ Checking git repository...")
    git_dir = ROOT / ".git"
    if not git_dir.exists():
        issues.append("Git repository not initialized - run 'git init'")
    else:
        print("  ✓ Git repository initialized")
    
    # 5. Check environment files
    print("\n✓ Checking deployment configs...")
    for config in ["Procfile", "runtime.txt", ".gitignore"]:
        if (ROOT / config).exists():
            print(f"  ✓ {config}")
    
    # Summary
    print("\n" + "=" * 50)
    if issues:
        print("\n❌ DEPLOYMENT BLOCKED - Fix these issues:")
        for issue in issues:
            print(f"  • {issue}")
    else:
        print("\n✅ ALL CRITICAL CHECKS PASSED!")
    
    if warnings:
        print("\n⚠️  Warnings (non-blocking):")
        for warning in warnings:
            print(f"  • {warning}")
    
    print("\n" + "=" * 50)
    
    if not issues:
        print("\n🚀 Project is ready for deployment!")
        print("\nNext steps:")
        print("1. Push to GitHub: See DEPLOY_NOW.md Step 1")
        print("2. Deploy backend to Render: See DEPLOY_NOW.md Step 2")
        print("3. Deploy frontend to Vercel: See DEPLOY_NOW.md Step 3")
        print("\n📖 Full guide: DEPLOYMENT_GUIDE.md")
    
    return len(issues) == 0

if __name__ == "__main__":
    success = check_deployment_readiness()
    sys.exit(0 if success else 1)
