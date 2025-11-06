using dnlib.DotNet;

namespace PEGASUS.Design.RenamingObfuscation.Overkill.Utils
{
	public static class MemberRenamer
	{
		public static void Rename(this IMemberDef member, string name)
		{
			member.Name = name;
		}

		public static void GetRenamed(this IMemberDef member)
		{
			member.Rename(Randomizer.GenerateRandomString(StringLength()));
		}

		public static int StringLength()
		{
			return Randomizer.Next(70, 50);
		}
	}
}
