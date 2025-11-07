using dnlib.DotNet;

namespace PEGASUS.Design.RenamingObfuscation.Overkill.Utils.Analyzer
{
	public class EventDefAnalyzer : DefAnalyzer
	{
		public override bool Execute(object context)
		{
			if (((EventDef)context).IsRuntimeSpecialName)
			{
				return false;
			}
			return true;
		}
	}
}
