##!/usr/bin/env python3

"""
Main script for generating multimodal research reports
"""

import asyncio
import sys
import argparse
from pathlib import Path
import os

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils.config import load_config
from utils.logger import setup_logger
from pipeline import MultimodalReportPipeline

async def main():
    """Main function"""
    
    # Set up argument parsing
    parser = argparse.ArgumentParser(
        description="Generate comprehensive multimodal research reports",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/generate_report.py --topic "Climate Change Impact on Agriculture"
  python scripts/generate_report.py --topic "AI in Healthcare" --config configs/healthcare_report.yaml
  python scripts/generate_report.py --topic "Future of Electric Vehicles" --output custom_output_dir
        """
    )
    
    parser.add_argument(
        "--topic",
        required=True,
        help="Research topic to generate report about"
    )
    
    parser.add_argument(
        "--config",
        default="configs/base.yaml",
        help="Configuration file path (default: configs/base.yaml)"
    )
    
    parser.add_argument(
        "--output",
        help="Output directory (default: auto-generated timestamp)"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Set up logging
    log_level = "DEBUG" if args.verbose else "INFO"
    logger = setup_logger("main", log_level)
    
    try:
        # Load configuration
        logger.info(f"Loading configuration from {args.config}")
        config = load_config(args.config)
        
        # Validate API key
        if not os.getenv('OPENAI_API_KEY'):
            logger.error("OPENAI_API_KEY environment variable not set!")
            logger.info("Please copy .env.example to .env and add your API key")
            return 1
        
        # Create pipeline
        logger.info("Initializing report generation pipeline")
        pipeline = MultimodalReportPipeline(config)
        
        # Generate report
        logger.info(f"Starting report generation for topic: {args.topic}")
        results = await pipeline.generate_report(args.topic)
        
        if not results.get('success', False):
            logger.error(f"Report generation failed: {results.get('error', 'Unknown error')}")
            return 1
        
        # Save results
        output_path = await pipeline.save_results(results, args.output)
        
        # Print summary
        logger.info("=" * 60)
        logger.info("🎉 REPORT GENERATION COMPLETE!")
        logger.info("=" * 60)
        logger.info(f"📁 Output directory: {output_path}")
        logger.info(f"📝 Word count: {results['report']['word_count']:,}")
        logger.info(f"📊 Charts created: {results['charts']['chart_count']}")
        logger.info(f"📚 Sources used: {results['research_data']['source_count']}")
        logger.info(f"⏱️  Generation time: {results['generation_time_seconds']:.1f} seconds")
        logger.info("=" * 60)
        logger.info(f"📖 View your report: {output_path}/final_report.html")
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("Report generation cancelled by user")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        if args.verbose:
            import traceback
            logger.error(traceback.format_exc())
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)