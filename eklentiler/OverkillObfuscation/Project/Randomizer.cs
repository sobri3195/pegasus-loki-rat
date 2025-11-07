using System.Security.Cryptography;
using System.Text;

namespace PEGASUS.Design.RenamingObfuscation.Overkill.Utils
{
	public class Randomizer
	{
		private static readonly RandomNumberGenerator csp = RandomNumberGenerator.Create();

		private static readonly char[] chars = "ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩαβγδεζηθικλμνξοπρστυφχψωABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzابتثجحخدذرزسشصضطظعغفقكلمنهويابتثجحخدذرزسشصضطظعغفقكلمنهوي0123456789艾诶比西迪伊弗吉尺杰开勒马娜哦屁吉吾儿丝提伊吾维豆贝尔维克斯吾贼德אבגדהוזחטיכךלמםנןסעפףצץקרשתאבגדהוזחטיכךלמםנןסעפףצץקרשת".ToCharArray();

		public static int Next(int maxValue, int minValue = 0)
		{
			if (minValue >= maxValue)
			{
				throw new ArgumentOutOfRangeException("minValue");
			}
			long num = (long)maxValue - (long)minValue;
			long num2 = 4294967295L / num * num;
			uint num3;
			do
			{
				num3 = RandomUInt();
			}
			while (num3 >= num2);
			return (int)(minValue + (long)num3 % num);
		}

		public static string GenerateRandomString(int size)
		{
			byte[] array = new byte[4 * size];
			csp.GetNonZeroBytes(array);
			StringBuilder stringBuilder = new StringBuilder(size);
			for (int i = 0; i < size; i++)
			{
				stringBuilder.Append(chars[(long)BitConverter.ToUInt32(array, i * 4) % (long)chars.Length]);
			}
			return stringBuilder.ToString();
		}

		private static uint RandomUInt()
		{
			return BitConverter.ToUInt32(RandomBytes(4), 0);
		}

		private static byte[] RandomBytes(int bytesNumber)
		{
			byte[] array = new byte[bytesNumber];
			csp.GetNonZeroBytes(array);
			return array;
		}
	}
}
