using System.Text;

namespace PEGASUS.Design.RenamingObfuscation.Overkill.Utils
{
	public static class StringDecoder
	{
		public static string Decrypt(string text, int key)
		{
			StringBuilder stringBuilder = new StringBuilder(text);
			StringBuilder stringBuilder2 = new StringBuilder(text.Length);
			for (int i = 0; i < text.Length; i++)
			{
				char c = stringBuilder[i];
				c = (char)(c ^ key);
				stringBuilder2.Append(c);
			}
			return stringBuilder2.ToString();
		}
	}
}
