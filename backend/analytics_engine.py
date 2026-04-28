"""
Analytics Engine - Generate reports and insights
Motor de Análisis - Generar reportes e insights
"""

import logging
from datetime import datetime
import statistics

logger = logging.getLogger(__name__)


class AnalyticsEngine:
    """Generate analytical reports and insights"""

    def __init__(self):
        pass

    def generate_report(self, analysis_results, report_type='comprehensive'):
        """Generate analysis report"""
        try:
            report = {
                'report_type': report_type,
                'generated_at': datetime.now().isoformat(),
                'analysis_results': analysis_results,
                'insights': self.extract_insights(analysis_results),
                'recommendations': self.generate_recommendations(analysis_results)
            }
            return report
        except Exception as e:
            logger.error(f"Report generation error: {str(e)}")
            return {'error': str(e)}

    def extract_insights(self, results):
        """Extract key insights from analysis"""
        try:
            insights = {
                'crowd_analysis': {},
                'incident_analysis': {},
                'operational_insights': {}
            }

            # Crowd insights
            if 'average_density' in results:
                insights['crowd_analysis']['average_density'] = results['average_density']
                if results['average_density'] > 5:
                    insights['crowd_analysis']['note'] = 'High crowd density detected'

            if 'peak_density' in results:
                insights['crowd_analysis']['peak_density'] = results['peak_density']

            # Incident insights
            if 'incidents_detected' in results:
                insights['incident_analysis']['total_incidents'] = results['incidents_detected']
                if results['incidents_detected'] > 0:
                    insights['incident_analysis']['action_required'] = True

            if 'critical_alerts' in results:
                insights['incident_analysis']['critical_alerts_count'] = len(results['critical_alerts'])

            # Operational insights
            if 'total_frames' in results:
                insights['operational_insights']['frames_analyzed'] = results['total_frames']

            return insights
        except Exception as e:
            logger.error(f"Insight extraction error: {str(e)}")
            return {}

    def generate_recommendations(self, results):
        """Generate recommendations based on analysis"""
        try:
            recommendations = []

            if 'average_density' in results:
                if results['average_density'] > 7:
                    recommendations.append({
                        'priority': 'high',
                        'category': 'crowd_management',
                        'recommendation': 'Implement crowd control measures. Density is above safe threshold.',
                        'affected_metric': 'average_density'
                    })
                elif results['average_density'] > 5:
                    recommendations.append({
                        'priority': 'medium',
                        'category': 'crowd_management',
                        'recommendation': 'Monitor crowd density. Consider opening additional exits.',
                        'affected_metric': 'average_density'
                    })

            if 'peak_density' in results:
                if results['peak_density'] > 10:
                    recommendations.append({
                        'priority': 'critical',
                        'category': 'safety',
                        'recommendation': 'Emergency crowd control required. Peak density is critical.',
                        'affected_metric': 'peak_density'
                    })

            if 'critical_alerts' in results and len(results['critical_alerts']) > 0:
                recommendations.append({
                    'priority': 'critical',
                    'category': 'security',
                    'recommendation': f"Address {len(results['critical_alerts'])} critical incidents immediately.",
                    'affected_metric': 'critical_alerts'
                })

            if 'incidents_detected' in results and results['incidents_detected'] > 5:
                recommendations.append({
                    'priority': 'high',
                    'category': 'security',
                    'recommendation': 'Multiple incidents detected. Review security protocols.',
                    'affected_metric': 'incidents_detected'
                })

            return recommendations
        except Exception as e:
            logger.error(f"Recommendation generation error: {str(e)}")
            return []

    def compare_analyses(self, analysis1, analysis2):
        """Compare two analysis results"""
        try:
            comparison = {
                'analysis1_density': analysis1.get('average_density', 0),
                'analysis2_density': analysis2.get('average_density', 0),
                'density_change': analysis2.get('average_density', 0) - analysis1.get('average_density', 0),
                'trend': 'increasing' if analysis2.get('average_density', 0) > analysis1.get('average_density', 0) else 'decreasing'
            }
            return comparison
        except Exception as e:
            logger.error(f"Comparison error: {str(e)}")
            return {}

    def calculate_statistics(self, values):
        """Calculate statistics from values"""
        try:
            if not values:
                return {}

            return {
                'mean': statistics.mean(values),
                'median': statistics.median(values),
                'stdev': statistics.stdev(values) if len(values) > 1 else 0,
                'min': min(values),
                'max': max(values),
                'count': len(values)
            }
        except Exception as e:
            logger.error(f"Statistics calculation error: {str(e)}")
            return {}
