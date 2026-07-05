using System;
using System.Net.Http;
using System.Security.Cryptography;
using System.Text;
using System.Threading.Tasks;

public class IPMasker
{
    private readonly string layer1Salt = "first-layer-salt-2025";
    private readonly string layer2Salt = "second-layer-salt-2025";
    private readonly string layer3Salt = "third-layer-salt-2025";

    public class MaskResult
    {
        public string Original { get; set; }
        public string Layer1 { get; set; }
        public string Layer2 { get; set; }
        public string Layer3 { get; set; }
        public DateTime Timestamp { get; set; }
    }

    private readonly HttpClient _httpClient = new HttpClient();

    public async Task<string> GetPublicIP()
    {
        var response = await _httpClient.GetStringAsync("https://api.ipsimple.org/ipv4");
        return response.Trim();
    }

    public string Sha256Hash(string data, string salt)
    {
        string input = data + salt;
        using (SHA256 sha256 = SHA256.Create())
        {
            byte[] bytes = Encoding.UTF8.GetBytes(input);
            byte[] hash = sha256.ComputeHash(bytes);
            
            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < hash.Length; i++)
            {
                sb.Append(hash[i].ToString("x2"));
            }
            return sb.ToString();
        }
    }

    public MaskResult MaskIP(string ip)
    {
        Console.WriteLine($"Original IP: {ip}");

        string layer1 = Sha256Hash(ip, layer1Salt);
        Console.WriteLine($"Layer 1 Hash: {layer1}");

        string layer2 = Sha256Hash(layer1, layer2Salt);
        Console.WriteLine($"Layer 2 Hash: {layer2}");

        string layer3 = Sha256Hash(layer2, layer3Salt);
        Console.WriteLine($"Layer 3 Hash: {layer3}");

        return new MaskResult
        {
            Original = ip,
            Layer1 = layer1,
            Layer2 = layer2,
            Layer3 = layer3,
            Timestamp = DateTime.UtcNow
        };
    }

    public async Task<MaskResult> GetAndMaskIP()
    {
        string ip = await GetPublicIP();
        return MaskIP(ip);
    }

    public static async Task Main(string[] args)
    {
        IPMasker masker = new IPMasker();

        Console.WriteLine("=== 3-Layer SHA-256 IP Masking System ===");
        Console.WriteLine("Detecting and masking current IP address...\n");

        try
        {
            MaskResult result = await masker.GetAndMaskIP();

            Console.WriteLine("\n=== Final Result ===");
            Console.WriteLine($"Original IP: {result.Original}");
            Console.WriteLine($"Final Masked IP: {result.Layer3}");
            Console.WriteLine($"Timestamp: {result.Timestamp:yyyy-MM-dd HH:mm:ss} UTC");

            Console.WriteLine("\n=== Network Encryption Simulation ===");
            Console.WriteLine("Packet routing through encrypted layers:");
            Console.WriteLine($"[Network] --> Layer1: {result.Layer1.Substring(0, 16)}...");
            Console.WriteLine($"[Layer1] --> Layer2: {result.Layer2.Substring(0, 16)}...");
            Console.WriteLine($"[Layer2] --> Layer3: {result.Layer3.Substring(0, 16)}...");
            Console.WriteLine("[Layer3] --> Internet (Fully Encrypted)");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error: {ex.Message}");
        }
    }
}
