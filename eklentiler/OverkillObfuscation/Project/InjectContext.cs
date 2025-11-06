using dnlib.DotNet;

namespace PEGASUS.Design.RenamingObfuscation.Overkill.Utils
{
	public class InjectContext
	{
		public readonly Dictionary<IDnlibDef, IDnlibDef> Map = new Dictionary<IDnlibDef, IDnlibDef>();

		public readonly ModuleDef OriginModule;

		public readonly ModuleDef TargetModule;

		public Importer Importer { get; }

		public InjectContext(ModuleDef module, ModuleDef target)
		{
			OriginModule = module;
			TargetModule = target;
			Importer = new Importer(target, ImporterOptions.TryToUseTypeDefs);
		}
	}
}
