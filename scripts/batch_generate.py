##!/usr/bin/env python3
"""
Batch processing script for generating multiple reports
"""

import asyncio
import sys
from pathlib import Path
import argparse
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils.config import load_config
from utils.logger import setup_logger
from pipeline import MultimodalReportPipeline

async def process_topic(pipeline: MultimodalReportPipeline, topic: str, output_base: str, logger) -> dict:
    """Process a single topic"""
    
    logger.info(f"🚀 Starting: {topic}")
    
    try:
        # Generate report
        results = await pipeline.generate_report(topic)
        
        if results.get('success'):
            # Create topic-specific output directory
            safe_topic = "".join(c for c in topic if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_topic = safe_topic.replace(' ', '_')[:50]  # Limit length
            topic_output = f"{output_base}/{safe_topic}"
            
            # Save results
            output_path = await pipeline.save_results(results, topic_output)
            
            logger.info(f"✅ Completed: {topic} -> {output_path}")
            return {
                'topic': topic,
                'success': True,
                'output_path': output_path,
                'word_count': results['report']['word_count'],
                'chart_count': results['charts']['chart_count'],
                'generation_time': results['generation_time_seconds']
            }
        else:
            logger.error(f"❌ Failed: {topic} - {results.get('error', 'Unknown error')}")
            return {
                'topic': topic,
                'success': False,
                'error': results.get('error', 'Unknown error')
            }
            
    except Exception as e:
        logger.error(f"❌ Exception for {topic}: {e}")
        return {
            'topic': topic,
            'success': False,
            'error': str(e)
        }

async def main():
    """Main batch processing function"""
    
    parser = argparse.ArgumentParser(description="Generate multiple reports in batch")
    
    parser.add_argument(
        "--topics-file",
        required=True,
        help="File containing topics (one per line)"
    )
    
    parser.add_argument(
        "--config",
        default="configs/base.yaml",
        help="Configuration file"
    )
    
    parser.add_argument(
        "--output-base",
        help="Base output directory (default: batch_reports_TIMESTAMP)"
    )
    
    parser.add_argument(
        "--concurrent",
        type=int,
        default=2,
        help="Number of concurrent report generations (default: 2)"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true"
    )
    
    args = parser.parse_args()
    
    # Setup
    logger = setup_logger("batch", "DEBUG" if args.verbose else "INFO")
    
    # Load topics
    topics_file = Path(args.topics_file)
    if not topics_file.exists():
        logger.error(f"Topics file not found: {topics_file}")
        return 1
    
    with open(topics_file, 'r', encoding='utf-8') as f:
        topics = [line.strip() for line in f if line.strip()]
    
    if not topics:
        logger.error("No topics found in file")
        return 1
    
    logger.info(f"Found {len(topics)} topics to process")
    
    # Setup output directory
    if args.output_base is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.output_base = f"outputs/batch_reports_{timestamp}"
    
    # Load config and create pipeline
    config = load_config(args.config)
    pipeline = MultimodalReportPipeline(config)
    
    # Process topics with concurrency limit
    semaphore = asyncio.Semaphore(args.concurrent)
    
    async def bounded_process(topic):
        async with semaphore:
            return await process_topic(pipeline, topic, args.output_base, logger)
    
    # Execute all tasks
    logger.info(f"Starting batch processing with {args.concurrent} concurrent workers")
    start_time = datetime.now()
    
    results = await asyncio.gather(*[bounded_process(topic) for topic in topics])
    
    end_time = datetime.now()
    total_time = end_time - start_time
    
    # Summary
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    logger.info("=" * 60)
    logger.info("📊 BATCH PROCESSING COMPLETE")
    logger.info("=" * 60)
    logger.info(f"✅ Successful: {len(successful)}")
    logger.info(f"❌ Failed: {len(failed)}")
    logger.info(f"⏱️  Total time: {total_time.total_seconds():.1f} seconds")
    
    if successful:
        total_words = sum(r['word_count'] for r in successful)
        total_charts = sum(r['chart_count'] for r in successful)
        logger.info(f"📝 Total words: {total_words:,}")
        logger.info(f"📊 Total charts: {total_charts}")
        logger.info(f"📁 Output base: {args.output_base}")
    
    if failed:
        logger.info("\n❌ Failed topics:")
        for result in failed:
            logger.info(f"  - {result['topic']}: {result['error']}")
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
