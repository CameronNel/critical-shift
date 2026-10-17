using System;
using System.Collections.Generic;
using System.Globalization;
using System.Text;

namespace CriticalShift.Content.Editor
{
    /// <summary>Reads the bake manifests (materials.json, lights.json). JsonUtility cannot read their name-keyed objects.
    /// Objects become Dictionary&lt;string, object&gt;, arrays List&lt;object&gt;, numbers double.</summary>
    internal static class MiniJson
    {
        public static object Parse(string text)
        {
            int i = 0;
            object value = ReadValue(text, ref i);
            SkipSpace(text, ref i);
            if (i != text.Length) throw new FormatException("Unexpected text after JSON value at " + i);
            return value;
        }

        static void SkipSpace(string s, ref int i)
        {
            while (i < s.Length && char.IsWhiteSpace(s[i])) i++;
        }

        static object ReadValue(string s, ref int i)
        {
            SkipSpace(s, ref i);
            if (i >= s.Length) throw new FormatException("Unexpected end of JSON");
            char c = s[i];
            if (c == '{') return ReadObject(s, ref i);
            if (c == '[') return ReadArray(s, ref i);
            if (c == '"') return ReadString(s, ref i);
            if (Match(s, ref i, "true")) return true;
            if (Match(s, ref i, "false")) return false;
            if (Match(s, ref i, "null")) return null;
            if (Match(s, ref i, "NaN")) return double.NaN;
            return ReadNumber(s, ref i);
        }

        static bool Match(string s, ref int i, string word)
        {
            if (string.CompareOrdinal(s, i, word, 0, word.Length) != 0) return false;
            i += word.Length;
            return true;
        }

        static Dictionary<string, object> ReadObject(string s, ref int i)
        {
            var result = new Dictionary<string, object>();
            i++;
            SkipSpace(s, ref i);
            if (s[i] == '}') { i++; return result; }
            while (true)
            {
                SkipSpace(s, ref i);
                string key = ReadString(s, ref i);
                SkipSpace(s, ref i);
                if (s[i] != ':') throw new FormatException("Expected ':' at " + i);
                i++;
                result[key] = ReadValue(s, ref i);
                SkipSpace(s, ref i);
                if (s[i] == ',') { i++; continue; }
                if (s[i] == '}') { i++; return result; }
                throw new FormatException("Expected ',' or '}' at " + i);
            }
        }

        static List<object> ReadArray(string s, ref int i)
        {
            var result = new List<object>();
            i++;
            SkipSpace(s, ref i);
            if (s[i] == ']') { i++; return result; }
            while (true)
            {
                result.Add(ReadValue(s, ref i));
                SkipSpace(s, ref i);
                if (s[i] == ',') { i++; continue; }
                if (s[i] == ']') { i++; return result; }
                throw new FormatException("Expected ',' or ']' at " + i);
            }
        }

        static string ReadString(string s, ref int i)
        {
            if (s[i] != '"') throw new FormatException("Expected string at " + i);
            i++;
            var sb = new StringBuilder();
            while (s[i] != '"')
            {
                char c = s[i++];
                if (c != '\\') { sb.Append(c); continue; }
                char e = s[i++];
                switch (e)
                {
                    case 'n': sb.Append('\n'); break;
                    case 't': sb.Append('\t'); break;
                    case 'r': sb.Append('\r'); break;
                    case 'b': sb.Append('\b'); break;
                    case 'f': sb.Append('\f'); break;
                    case 'u': sb.Append((char)Convert.ToInt32(s.Substring(i, 4), 16)); i += 4; break;
                    default: sb.Append(e); break;
                }
            }
            i++;
            return sb.ToString();
        }

        static double ReadNumber(string s, ref int i)
        {
            int start = i;
            while (i < s.Length && "+-0123456789.eE".IndexOf(s[i]) >= 0) i++;
            if (start == i) throw new FormatException("Unexpected character '" + s[i] + "' at " + i);
            return double.Parse(s.Substring(start, i - start), NumberStyles.Float, CultureInfo.InvariantCulture);
        }
    }
}
