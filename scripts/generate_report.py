# The main function that coordinates everything
async def main():
    # Get user input
    parser = argparse.ArgumentParser(description="Generate reports")
    parser.add_argument("--topic", required=True, help="What to write about")
    parser.add_argument("--config", default="configs/base.yaml", help="Settings file")
    
    args = parser.parse_args()
    
    # Load settings
    config = load_config(args.config)
    
    # Create the pipeline (assembly line)
    pipeline = MultimodalReportPipeline(config)
    
    # Generate the report
    results = await pipeline.generate_report(topic=args.topic)
    
    # Save the results
    await pipeline.save_results(results, output_directory)

class MultimodalReportPipeline:
    async def generate_report(self, topic):
        """The complete assembly line"""
        
        # Stage 1: Research (find information)
        print("🔍 Researching topic...")
        research_data = await self.research_agent.research_topic(topic)
        
        # Stage 2: Plan (organize information)
        print("📋 Planning report structure...")
        plan = await self.planning_agent.create_outline(research_data, topic)
        
        # Stage 3: Visualize (create charts)
        print("📊 Creating visualizations...")
        charts = await self.viz_agent.generate_charts(research_data, plan)
        
        # Stage 4: Generate (write report)
        print("✍️ Writing final report...")
        report = await self.generation_agent.write_report(research_data, plan, charts)
        
        # Stage 5: Evaluate (check quality)
        print("🔍 Evaluating report quality...")
        evaluation = await self.evaluator.assess_quality(report)
        
        return {
            "research_data": research_data,
            "plan": plan,
            "charts": charts,
            "report": report,
            "evaluation": evaluation
        }