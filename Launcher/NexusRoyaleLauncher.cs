// Instalador e launcher do Nexus Royale: um .exe só.
//
// - Aberto de fora de uma instalação (o NexusRoyale-Instalador.exe baixado da Release), mostra a tela de
//   instalação: escolhe a pasta, copia a si mesmo para <pasta>\NexusRoyaleLauncher.exe, cria os atalhos e
//   registra o jogo em "Aplicativos" do Windows (para desinstalar).
// - Aberto da instalação (o atalho "Nexus Royale"), confere a última Release de holaluiz/MOBA-BR no GitHub.
//   Se houver versão nova, baixa, confere o SHA-256, instala na pasta "game" e só então abre o jogo. Sem
//   internet, abre a versão instalada. Se a Release trouxer um launcher mais novo, troca a si mesmo antes.
//
// O pacote de cada versão é feito pelo Unreal/ue_release.py (manifest.json + zip em partes de até 1,9 GB).
// Compilar: python -I Unreal/ue_release.py launcher (usa o csc do .NET Framework 4, que vem no Windows;
// por isso o código é C# 5: sem $"", ?. nem nameof).
//
// Opções na linha de comando: /desinstalar, /instalar (mostra a instalação de novo), /semAtualizar,
// /forcar (baixa a versão de novo), /soAtualizar (não abre o jogo). O resto vai para o NexusRoyale.exe.
//
// O repositório é privado, então é preciso um token do GitHub com leitura em holaluiz/MOBA-BR. Ordem:
// variável NEXUS_GH_TOKEN, token.dat (criptografado com o DPAPI do usuário), token.txt e "gh auth token".

using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Drawing;
using System.IO;
using System.IO.Compression;
using System.Net;
using System.Reflection;
using System.Security.Cryptography;
using System.Text;
using System.Threading;
using System.Web.Script.Serialization;
using System.Windows.Forms;
using Microsoft.Win32;

[assembly: AssemblyTitle("Nexus Royale Launcher")]
[assembly: AssemblyProduct("Nexus Royale")]
[assembly: AssemblyDescription("Instala, atualiza e abre o Nexus Royale")]
[assembly: AssemblyVersion("1.0.0.0")]
[assembly: AssemblyFileVersion("1.0.0.0")]

namespace NexusRoyale
{
    static class Programa
    {
        public const string Versao = "1.0.0";   // o ue_release.py lê esta linha para o manifest.json
        public const string Repo = "holaluiz/MOBA-BR";
        public const string NomeExe = "NexusRoyaleLauncher.exe";
        public const string Marca = ".nexus-instalado";
        public const string ChaveDesinstalar = @"Software\Microsoft\Windows\CurrentVersion\Uninstall\NexusRoyale";

        public static string Pasta { get { return Path.GetDirectoryName(Application.ExecutablePath); } }
        public static string[] Args = new string[0];

        public static bool TemOpcao(string nome)
        {
            foreach (string a in Args)
                if (string.Equals(a.TrimStart('-', '/'), nome, StringComparison.OrdinalIgnoreCase)) return true;
            return false;
        }

        public static string ArgsDoJogo()
        {
            string[] nossas = { "desinstalar", "instalar", "semAtualizar", "forcar", "soAtualizar" };
            StringBuilder sb = new StringBuilder();
            foreach (string a in Args)
            {
                bool nossa = false;
                foreach (string n in nossas)
                    if (string.Equals(a.TrimStart('-', '/'), n, StringComparison.OrdinalIgnoreCase)) nossa = true;
                if (nossa) continue;
                if (sb.Length > 0) sb.Append(' ');
                sb.Append(a.Contains(" ") ? "\"" + a + "\"" : a);
            }
            return sb.ToString();
        }

        [STAThread]
        static int Main(string[] args)
        {
            Args = args;
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            ServicePointManager.SecurityProtocol = (SecurityProtocolType)3072;   // TLS 1.2

            if (TemOpcao("desinstalar")) { Instalacao.Desinstalar(); return 0; }

            bool instalado = File.Exists(Path.Combine(Pasta, Marca));
            if (!instalado && !TemOpcao("instalar"))
            {
                // O instalador foi aberto de novo, mas o jogo já está instalado: abre a instalação existente.
                string existente = Instalacao.PastaRegistrada();
                if (existente != null && File.Exists(Path.Combine(existente, NomeExe)) &&
                    !string.Equals(Path.GetFullPath(existente), Path.GetFullPath(Pasta), StringComparison.OrdinalIgnoreCase))
                {
                    Process.Start(new ProcessStartInfo(Path.Combine(existente, NomeExe), ArgsDoJogo()) { WorkingDirectory = existente });
                    return 0;
                }
            }
            Application.Run(new Janela(instalado && !TemOpcao("instalar")));
            return 0;
        }
    }

    // --- erros com mensagem para o jogador -----------------------------------------------------------

    class ErroAcesso : Exception { public ErroAcesso(string m) : base(m) { } }
    class ErroSemVersao : Exception { public ErroSemVersao(string m) : base(m) { } }
    class ErroRede : Exception { public ErroRede(string m) : base(m) { } }
    class Cancelado : Exception { public Cancelado() : base("Cancelado.") { } }

    // --- token do GitHub ------------------------------------------------------------------------------

    static class Token
    {
        static readonly byte[] Entropia = Encoding.UTF8.GetBytes("NexusRoyale.Launcher");

        public static string Pegar(string pasta)
        {
            string t = Environment.GetEnvironmentVariable("NEXUS_GH_TOKEN");
            if (!string.IsNullOrWhiteSpace(t)) return t.Trim();
            try
            {
                string dat = Path.Combine(pasta, "token.dat");
                if (File.Exists(dat))
                {
                    byte[] b = ProtectedData.Unprotect(File.ReadAllBytes(dat), Entropia, DataProtectionScope.CurrentUser);
                    t = Encoding.UTF8.GetString(b).Trim();
                    if (t.Length > 0) return t;
                }
            }
            catch { }
            try
            {
                string txt = Path.Combine(pasta, "token.txt");
                if (File.Exists(txt))
                {
                    t = File.ReadAllText(txt).Trim();
                    if (t.Length > 0) return t;
                }
            }
            catch { }
            return DoGh();
        }

        // O login do GitHub CLI, que já existe no PC de quem desenvolve.
        public static string DoGh()
        {
            try
            {
                ProcessStartInfo i = new ProcessStartInfo("gh", "auth token");
                i.UseShellExecute = false; i.CreateNoWindow = true;
                i.RedirectStandardOutput = true; i.RedirectStandardError = true;
                using (Process p = Process.Start(i))
                {
                    string saida = p.StandardOutput.ReadToEnd().Trim();
                    if (!p.WaitForExit(8000)) { try { p.Kill(); } catch { } return null; }
                    if (p.ExitCode == 0 && saida.Length > 0) return saida;
                }
            }
            catch { }
            return null;
        }

        public static void Salvar(string pasta, string token)
        {
            byte[] b = ProtectedData.Protect(Encoding.UTF8.GetBytes(token.Trim()), Entropia, DataProtectionScope.CurrentUser);
            File.WriteAllBytes(Path.Combine(pasta, "token.dat"), b);
            string txt = Path.Combine(pasta, "token.txt");
            if (File.Exists(txt)) File.Delete(txt);
        }
    }

    // --- GitHub -------------------------------------------------------------------------------------

    static class GitHub
    {
        static readonly JavaScriptSerializer Json = new JavaScriptSerializer { MaxJsonLength = int.MaxValue };

        static HttpWebRequest Api(string url, string token)
        {
            HttpWebRequest p = (HttpWebRequest)WebRequest.Create(url);
            p.UserAgent = "NexusRoyale-Launcher/" + Programa.Versao;
            p.Accept = "application/vnd.github+json";
            p.Headers["X-GitHub-Api-Version"] = "2022-11-28";
            if (token != null) p.Headers["Authorization"] = "Bearer " + token;
            p.Timeout = 20000;
            p.ReadWriteTimeout = 30000;
            return p;
        }

        static int Codigo(WebException e)
        {
            HttpWebResponse r = e.Response as HttpWebResponse;
            return r == null ? 0 : (int)r.StatusCode;
        }

        static string LerTudo(WebResponse r)
        {
            using (StreamReader s = new StreamReader(r.GetResponseStream(), Encoding.UTF8)) return s.ReadToEnd();
        }

        public static Dictionary<string, object> UltimaRelease(string token)
        {
            try
            {
                using (WebResponse r = Api("https://api.github.com/repos/" + Programa.Repo + "/releases/latest", token).GetResponse())
                    return (Dictionary<string, object>)Json.DeserializeObject(LerTudo(r));
            }
            catch (WebException e)
            {
                int c = Codigo(e);
                if (c == 401) throw new ErroAcesso("O GitHub recusou o token: ele venceu ou foi digitado errado.");
                if (c == 404)
                {
                    if (token == null)
                        throw new ErroAcesso("O repositório " + Programa.Repo + " é privado e não há token do GitHub neste PC.");
                    if (!TemAcesso(token))
                        throw new ErroAcesso("O token não tem acesso ao repositório " + Programa.Repo + ".");
                    throw new ErroSemVersao("Ainda não há nenhuma versão publicada.");
                }
                if (c == 403) throw new ErroRede("O GitHub limitou os pedidos por agora. Tente de novo em alguns minutos.");
                throw new ErroRede("Sem conexão com o GitHub (" + e.Message + ").");
            }
        }

        public static bool TemAcesso(string token)
        {
            try
            {
                using (Api("https://api.github.com/repos/" + Programa.Repo, token).GetResponse()) return true;
            }
            catch (WebException) { return false; }
        }

        public static Dictionary<string, object> Asset(Dictionary<string, object> rel, string nome)
        {
            object[] assets = rel["assets"] as object[];
            if (assets != null)
                foreach (object o in assets)
                {
                    Dictionary<string, object> a = (Dictionary<string, object>)o;
                    if (string.Equals((string)a["name"], nome, StringComparison.OrdinalIgnoreCase)) return a;
                }
            throw new Exception("A versão " + rel["tag_name"] + " não tem o arquivo " + nome + ".");
        }

        public static Dictionary<string, object> LerJson(string arquivo)
        {
            return (Dictionary<string, object>)Json.DeserializeObject(File.ReadAllText(arquivo, Encoding.UTF8));
        }

        // Baixa um arquivo da Release. A URL da API responde com um redirecionamento para o armazenamento do
        // GitHub; o token vai só no primeiro pedido. Retoma um download pela metade (Range).
        public static void Baixar(Dictionary<string, object> asset, string destino, string token, long total,
                                  Action<long, long> progresso, Func<bool> cancelar)
        {
            string real = null;
            int tentativas = 0;
            while (true)
            {
                try
                {
                    if (real == null)
                    {
                        HttpWebRequest p = Api((string)asset["url"], token);
                        p.Accept = "application/octet-stream";
                        p.AllowAutoRedirect = false;
                        using (HttpWebResponse r = (HttpWebResponse)p.GetResponse())
                        {
                            int c = (int)r.StatusCode;
                            if (c >= 300 && c < 400) real = r.Headers["Location"];
                            else { Copiar(r, destino, false, total, progresso, cancelar); return; }
                        }
                    }
                    long ja = File.Exists(destino) ? new FileInfo(destino).Length : 0;
                    if (ja >= total && total > 0) return;
                    HttpWebRequest q = (HttpWebRequest)WebRequest.Create(real);
                    q.UserAgent = "NexusRoyale-Launcher/" + Programa.Versao;
                    q.Timeout = 30000;
                    q.ReadWriteTimeout = 60000;
                    if (ja > 0) q.AddRange(ja);
                    using (HttpWebResponse r = (HttpWebResponse)q.GetResponse())
                        Copiar(r, destino, r.StatusCode == HttpStatusCode.PartialContent, total, progresso, cancelar);
                    return;
                }
                catch (Cancelado) { throw; }
                catch (WebException e)
                {
                    int c = Codigo(e);
                    if (c == 401 || c == 404) throw new ErroAcesso("O GitHub recusou o download de " + asset["name"] + ".");
                    if (c == 403 || c == 400) real = null;   // o link do armazenamento venceu: pede outro
                    if (++tentativas >= 5) throw new ErroRede("O download de " + asset["name"] + " falhou (" + e.Message + ").");
                    Thread.Sleep(2000 * tentativas);
                }
                catch (IOException e)
                {
                    if (++tentativas >= 5) throw new ErroRede("O download de " + asset["name"] + " falhou (" + e.Message + ").");
                    Thread.Sleep(2000 * tentativas);
                }
            }
        }

        static void Copiar(HttpWebResponse r, string destino, bool continuar, long total, Action<long, long> progresso,
                           Func<bool> cancelar)
        {
            byte[] buf = new byte[1 << 20];
            using (Stream entrada = r.GetResponseStream())
            using (FileStream saida = new FileStream(destino, continuar ? FileMode.Append : FileMode.Create, FileAccess.Write))
            {
                long feito = saida.Length;
                int n;
                while ((n = entrada.Read(buf, 0, buf.Length)) > 0)
                {
                    if (cancelar()) throw new Cancelado();
                    saida.Write(buf, 0, n);
                    feito += n;
                    progresso(feito, total);
                }
            }
        }
    }

    // --- instalação no Windows (atalhos, Aplicativos, desinstalar) -----------------------------------

    static class Instalacao
    {
        public static string PastaPadrao()
        {
            string sistema = Path.GetPathRoot(Environment.SystemDirectory);
            DriveInfo melhor = null;
            foreach (DriveInfo d in DriveInfo.GetDrives())
            {
                try
                {
                    if (d.DriveType != DriveType.Fixed || !d.IsReady) continue;
                    if (melhor == null || d.AvailableFreeSpace > melhor.AvailableFreeSpace) melhor = d;
                }
                catch { }
            }
            if (melhor == null || string.Equals(melhor.Name, sistema, StringComparison.OrdinalIgnoreCase))
                return Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "Programs", "NexusRoyale");
            return Path.Combine(melhor.Name, "Jogos", "NexusRoyale");
        }

        // A pasta escolhida sempre ganha a subpasta NexusRoyale: o desinstalar apaga só ela.
        public static string Normalizar(string pasta)
        {
            pasta = Path.GetFullPath(pasta.Trim().Trim('"'));
            if (!string.Equals(Path.GetFileName(pasta.TrimEnd('\\')), "NexusRoyale", StringComparison.OrdinalIgnoreCase))
                pasta = Path.Combine(pasta, "NexusRoyale");
            return pasta;
        }

        public static string PastaRegistrada()
        {
            using (RegistryKey k = Registry.CurrentUser.OpenSubKey(Programa.ChaveDesinstalar))
                return k == null ? null : k.GetValue("InstallLocation") as string;
        }

        static string AtalhoMenu
        {
            get { return Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.Programs), "Nexus Royale.lnk"); }
        }

        static string AtalhoDesktop
        {
            get { return Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.DesktopDirectory), "Nexus Royale.lnk"); }
        }

        static void CriarAtalho(string lnk, string alvo, string pasta)
        {
            Type t = Type.GetTypeFromProgID("WScript.Shell");
            object shell = Activator.CreateInstance(t);
            object s = t.InvokeMember("CreateShortcut", BindingFlags.InvokeMethod, null, shell, new object[] { lnk });
            Type ts = s.GetType();
            ts.InvokeMember("TargetPath", BindingFlags.SetProperty, null, s, new object[] { alvo });
            ts.InvokeMember("WorkingDirectory", BindingFlags.SetProperty, null, s, new object[] { pasta });
            ts.InvokeMember("IconLocation", BindingFlags.SetProperty, null, s, new object[] { alvo + ",0" });
            ts.InvokeMember("Description", BindingFlags.SetProperty, null, s, new object[] { "Nexus Royale (confere atualizações e abre o jogo)" });
            ts.InvokeMember("Save", BindingFlags.InvokeMethod, null, s, null);
        }

        public static string Instalar(string pasta, bool atalhoDesktop)
        {
            Directory.CreateDirectory(pasta);
            string exe = Path.Combine(pasta, Programa.NomeExe);
            if (!string.Equals(Path.GetFullPath(exe), Path.GetFullPath(Application.ExecutablePath), StringComparison.OrdinalIgnoreCase))
                File.Copy(Application.ExecutablePath, exe, true);
            File.WriteAllText(Path.Combine(pasta, Programa.Marca), Programa.Versao);

            CriarAtalho(AtalhoMenu, exe, pasta);
            if (atalhoDesktop) CriarAtalho(AtalhoDesktop, exe, pasta);

            using (RegistryKey k = Registry.CurrentUser.CreateSubKey(Programa.ChaveDesinstalar))
            {
                k.SetValue("DisplayName", "Nexus Royale");
                k.SetValue("Publisher", "holaluiz");
                k.SetValue("InstallLocation", pasta);
                k.SetValue("DisplayIcon", exe + ",0");
                k.SetValue("UninstallString", "\"" + exe + "\" /desinstalar");
                k.SetValue("NoModify", 1, RegistryValueKind.DWord);
                k.SetValue("NoRepair", 1, RegistryValueKind.DWord);
                if (k.GetValue("DisplayVersion") == null) k.SetValue("DisplayVersion", "0.0.0");
            }
            return exe;
        }

        public static void RegistrarVersao(string versao, long bytes)
        {
            using (RegistryKey k = Registry.CurrentUser.OpenSubKey(Programa.ChaveDesinstalar, true))
            {
                if (k == null) return;
                k.SetValue("DisplayVersion", versao);
                k.SetValue("EstimatedSize", (int)(bytes / 1024), RegistryValueKind.DWord);
            }
        }

        public static void Desinstalar()
        {
            string pasta = Programa.Pasta;
            if (!File.Exists(Path.Combine(pasta, Programa.Marca)))
            {
                MessageBox.Show("Este launcher não está numa pasta de instalação do Nexus Royale.", "Nexus Royale",
                                MessageBoxButtons.OK, MessageBoxIcon.Information);
                return;
            }
            if (Process.GetProcessesByName("NexusRoyale").Length > 0)
            {
                MessageBox.Show("Feche o jogo antes de desinstalar.", "Nexus Royale", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }
            if (MessageBox.Show("Desinstalar o Nexus Royale de\n" + pasta + "?\n\nO jogo e os downloads desta pasta serão apagados.",
                                "Nexus Royale", MessageBoxButtons.YesNo, MessageBoxIcon.Question) != DialogResult.Yes) return;
            try
            {
                foreach (string lnk in new string[] { AtalhoMenu, AtalhoDesktop })
                    if (File.Exists(lnk)) File.Delete(lnk);
                Registry.CurrentUser.DeleteSubKeyTree(Programa.ChaveDesinstalar, false);
                // Só o que o launcher criou: a pasta pode ter sido escolhida pelo jogador.
                foreach (string d in new string[] { "game", "game.novo", "game.antigo", "download" })
                {
                    string c = Path.Combine(pasta, d);
                    if (Directory.Exists(c)) Directory.Delete(c, true);
                }
                foreach (string a in new string[] { "token.dat", "token.txt", Programa.Marca, Programa.NomeExe + ".velho", Programa.NomeExe + ".novo" })
                {
                    string c = Path.Combine(pasta, a);
                    if (File.Exists(c)) File.Delete(c);
                }
                // O .exe em uso não se apaga sozinho: um cmd escondido apaga depois que ele fechar.
                ProcessStartInfo i = new ProcessStartInfo("cmd.exe",
                    "/c ping 127.0.0.1 -n 3 > nul & del /f /q \"" + Application.ExecutablePath + "\" & rmdir \"" + pasta + "\"");
                i.CreateNoWindow = true; i.UseShellExecute = false; i.WorkingDirectory = Path.GetTempPath();
                Process.Start(i);
                MessageBox.Show("O Nexus Royale foi desinstalado.", "Nexus Royale", MessageBoxButtons.OK, MessageBoxIcon.Information);
            }
            catch (Exception e)
            {
                MessageBox.Show("Não deu para desinstalar tudo: " + e.Message, "Nexus Royale", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }
    }

    // --- janela -------------------------------------------------------------------------------------

    class Janela : Form
    {
        static readonly Color Fundo = Color.FromArgb(20, 24, 38);
        static readonly Color Painel = Color.FromArgb(30, 35, 54);
        static readonly Color Ouro = Color.FromArgb(232, 182, 76);
        static readonly Color Texto = Color.FromArgb(225, 228, 238);
        static readonly Color Apagado = Color.FromArgb(150, 156, 176);

        readonly bool modoLauncher;
        readonly string pastaBase;
        Label status, detalhe, espaco;
        ProgressBar barra;
        Button botaoA, botaoB, botaoC;
        TextBox caixaPasta, caixaToken;
        CheckBox caixaDesktop;
        volatile bool cancelar;
        Thread trabalho;
        DateTime ultimoDesenho = DateTime.MinValue;
        DateTime inicioDownload;
        long baixadoAntes;

        string Jogo { get { return Path.Combine(pastaBase, "game"); } }
        string Baixados { get { return Path.Combine(pastaBase, "download"); } }
        string ExeJogo { get { return Path.Combine(Jogo, "NexusRoyale.exe"); } }

        public Janela(bool launcher)
        {
            modoLauncher = launcher;
            pastaBase = Programa.Pasta;
            Text = "Nexus Royale";
            FormBorderStyle = FormBorderStyle.FixedSingle;
            MaximizeBox = false;
            StartPosition = FormStartPosition.CenterScreen;
            BackColor = Fundo;
            ForeColor = Texto;
            Font = new Font("Segoe UI", 9.5f);
            ClientSize = new Size(560, launcher ? 210 : 330);
            try { Icon = Icon.ExtractAssociatedIcon(Application.ExecutablePath); } catch { }

            Label titulo = new Label();
            titulo.Text = "NEXUS ROYALE";
            titulo.Font = new Font("Segoe UI", 20f, FontStyle.Bold);
            titulo.ForeColor = Ouro;
            titulo.AutoSize = true;
            titulo.Location = new Point(22, 14);
            Controls.Add(titulo);

            Label sub = new Label();
            sub.Text = launcher ? "Launcher " + Programa.Versao : "Instalação · launcher " + Programa.Versao;
            sub.ForeColor = Apagado;
            sub.AutoSize = true;
            sub.Location = new Point(26, 56);
            Controls.Add(sub);

            if (launcher) MontarLauncher(); else MontarInstalador();
        }

        Button NovoBotao(string texto, int x, int y, int largura)
        {
            Button b = new Button();
            b.Text = texto;
            b.FlatStyle = FlatStyle.Flat;
            b.FlatAppearance.BorderColor = Ouro;
            b.BackColor = Painel;
            b.ForeColor = Texto;
            b.Location = new Point(x, y);
            b.Size = new Size(largura, 32);
            Controls.Add(b);
            return b;
        }

        Label NovoTexto(string texto, int x, int y, int largura, Color cor)
        {
            Label l = new Label();
            l.Text = texto;
            l.ForeColor = cor;
            l.AutoEllipsis = true;
            l.Location = new Point(x, y);
            l.Size = new Size(largura, 22);
            Controls.Add(l);
            return l;
        }

        // --- tela de instalação ---

        void MontarInstalador()
        {
            NovoTexto("Pasta de instalação (o jogo ocupa uns 3 GB, e o download precisa do dobro):", 24, 92, 520, Texto);
            caixaPasta = new TextBox();
            caixaPasta.Location = new Point(26, 118);
            caixaPasta.Size = new Size(400, 26);
            caixaPasta.BackColor = Painel;
            caixaPasta.ForeColor = Texto;
            caixaPasta.BorderStyle = BorderStyle.FixedSingle;
            string registrada = Instalacao.PastaRegistrada();
            caixaPasta.Text = registrada ?? Instalacao.PastaPadrao();
            caixaPasta.TextChanged += delegate { MostrarEspaco(); };
            Controls.Add(caixaPasta);
            Button alterar = NovoBotao("Alterar…", 436, 115, 100);
            alterar.Click += delegate
            {
                using (FolderBrowserDialog d = new FolderBrowserDialog())
                {
                    d.Description = "Escolha onde instalar (a subpasta NexusRoyale é criada dentro dela).";
                    if (d.ShowDialog(this) == DialogResult.OK) caixaPasta.Text = Instalacao.Normalizar(d.SelectedPath);
                }
            };
            espaco = NovoTexto("", 24, 148, 520, Apagado);
            MostrarEspaco();

            caixaDesktop = new CheckBox();
            caixaDesktop.Text = "Criar atalho na área de trabalho";
            caixaDesktop.Checked = true;
            caixaDesktop.AutoSize = true;
            caixaDesktop.Location = new Point(26, 176);
            Controls.Add(caixaDesktop);

            bool precisaToken = Token.Pegar(pastaBase) == null;
            if (precisaToken)
            {
                NovoTexto("Token do GitHub (o repositório " + Programa.Repo + " é privado):", 24, 210, 520, Texto);
                caixaToken = new TextBox();
                caixaToken.Location = new Point(26, 236);
                caixaToken.Size = new Size(400, 26);
                caixaToken.UseSystemPasswordChar = true;
                caixaToken.BackColor = Painel;
                caixaToken.ForeColor = Texto;
                caixaToken.BorderStyle = BorderStyle.FixedSingle;
                Controls.Add(caixaToken);
                LinkLabel como = new LinkLabel();
                como.Text = "Como criar";
                como.LinkColor = Ouro;
                como.AutoSize = true;
                como.Location = new Point(440, 239);
                como.LinkClicked += delegate { MostrarComoCriarToken(); };
                Controls.Add(como);
            }
            else
            {
                NovoTexto("Acesso ao GitHub: ok (token encontrado neste PC).", 24, 210, 520, Apagado);
            }

            status = NovoTexto("", 24, 284, 300, Apagado);
            botaoA = NovoBotao("Instalar", 436, 280, 100);
            botaoA.Click += delegate { Instalar(); };
            AcceptButton = botaoA;
        }

        void MostrarEspaco()
        {
            try
            {
                string raiz = Path.GetPathRoot(Path.GetFullPath(caixaPasta.Text));
                DriveInfo d = new DriveInfo(raiz);
                double livre = d.AvailableFreeSpace / 1073741824.0;
                espaco.Text = string.Format("Espaço livre em {0} {1:0.0} GB", raiz, livre);
                espaco.ForeColor = livre < 7 ? Color.FromArgb(240, 120, 100) : Apagado;
            }
            catch { espaco.Text = ""; }
        }

        static void MostrarComoCriarToken()
        {
            MessageBox.Show(
                "1. Entre no GitHub com uma conta que tenha acesso a " + Programa.Repo + ".\n" +
                "2. Abra github.com/settings/personal-access-tokens e clique em \"Generate new token\" (fine-grained).\n" +
                "3. Em \"Repository access\", escolha \"Only select repositories\" e marque " + Programa.Repo + ".\n" +
                "4. Em \"Permissions\", dê \"Contents: Read-only\" (só isso).\n" +
                "5. Gere, copie e cole aqui. O launcher guarda o token criptografado só para o seu usuário do Windows.",
                "Token do GitHub", MessageBoxButtons.OK, MessageBoxIcon.Information);
            try { Process.Start("https://github.com/settings/personal-access-tokens/new"); } catch { }
        }

        void Instalar()
        {
            string pasta;
            try { pasta = Instalacao.Normalizar(caixaPasta.Text); }
            catch { status.Text = "Pasta inválida."; return; }
            string token = caixaToken != null ? caixaToken.Text.Trim() : null;
            if (caixaToken != null && token.Length == 0) { status.Text = "Cole o token do GitHub."; return; }
            botaoA.Enabled = false;
            status.ForeColor = Apagado;
            status.Text = token != null ? "Conferindo o token…" : "Instalando…";
            Refresh();
            if (token != null && !GitHub.TemAcesso(token))
            {
                status.ForeColor = Color.FromArgb(240, 120, 100);
                status.Text = "Esse token não tem acesso ao " + Programa.Repo + ".";
                botaoA.Enabled = true;
                return;
            }
            try
            {
                string exe = Instalacao.Instalar(pasta, caixaDesktop.Checked);
                if (token != null) Token.Salvar(pasta, token);
                Process.Start(new ProcessStartInfo(exe, Programa.ArgsDoJogo()) { WorkingDirectory = pasta });
                Close();
            }
            catch (Exception e)
            {
                status.ForeColor = Color.FromArgb(240, 120, 100);
                status.Text = "Erro: " + e.Message;
                botaoA.Enabled = true;
            }
        }

        // --- tela do launcher ---

        void MontarLauncher()
        {
            status = NovoTexto("Procurando atualizações…", 24, 90, 512, Texto);
            barra = new ProgressBar();
            barra.Location = new Point(26, 118);
            barra.Size = new Size(510, 18);
            barra.Maximum = 1000;
            barra.Style = ProgressBarStyle.Marquee;
            Controls.Add(barra);
            detalhe = NovoTexto("", 24, 142, 512, Apagado);
            botaoA = NovoBotao("Tentar de novo", 26, 166, 150);
            botaoB = NovoBotao("Jogar mesmo assim", 186, 166, 170);
            botaoC = NovoBotao("Trocar token", 366, 166, 170);
            botaoA.Visible = botaoB.Visible = botaoC.Visible = false;
            botaoA.Click += delegate { Comecar(false); };
            botaoB.Click += delegate { Comecar(true); };
            botaoC.Click += delegate { if (PedirToken()) Comecar(false); };
            Shown += delegate { Comecar(Programa.TemOpcao("semAtualizar")); };
            FormClosing += delegate { cancelar = true; };
        }

        void NaTela(Action a)
        {
            if (IsDisposed) return;
            if (InvokeRequired) { try { BeginInvoke(a); } catch (InvalidOperationException) { } }
            else a();
        }

        void Status(string texto) { NaTela(delegate { status.Text = texto; detalhe.Text = ""; barra.Style = ProgressBarStyle.Marquee; }); }

        void Progresso(string texto, long feito, long total, bool velocidade)
        {
            if (total <= 0) return;
            DateTime agora = DateTime.Now;
            if (feito < total && (agora - ultimoDesenho).TotalMilliseconds < 150) return;
            ultimoDesenho = agora;
            string d = string.Format("{0:N0} de {1:N0} MB", feito / 1048576.0, total / 1048576.0);
            if (velocidade)
            {
                double seg = (agora - inicioDownload).TotalSeconds;
                if (seg > 1)
                {
                    double bps = (feito - baixadoAntes) / seg;
                    if (bps > 0)
                    {
                        double falta = (total - feito) / bps;
                        d += string.Format(" · {0:0.0} MB/s · faltam {1}", bps / 1048576.0,
                                           falta >= 90 ? Math.Ceiling(falta / 60) + " min" : Math.Ceiling(falta) + " s");
                    }
                }
            }
            int v = (int)Math.Min(1000, feito * 1000 / total);
            NaTela(delegate
            {
                status.Text = texto;
                detalhe.Text = d;
                barra.Style = ProgressBarStyle.Continuous;
                barra.Value = v;
            });
        }

        void Comecar(bool semAtualizar)
        {
            botaoA.Visible = botaoB.Visible = botaoC.Visible = false;
            status.ForeColor = Texto;
            cancelar = false;
            trabalho = new Thread(delegate () { Trabalhar(semAtualizar); });
            trabalho.IsBackground = true;
            trabalho.Start();
        }

        void Erro(string texto, bool acesso)
        {
            bool instalado = File.Exists(ExeJogo);
            NaTela(delegate
            {
                status.ForeColor = Color.FromArgb(240, 120, 100);
                status.Text = texto;
                detalhe.Text = instalado ? "Versão instalada: " + (VersaoInstalada() ?? "?") : "O jogo ainda não está instalado.";
                barra.Style = ProgressBarStyle.Continuous;
                barra.Value = 0;
                botaoA.Visible = true;
                botaoB.Visible = instalado;
                botaoC.Visible = acesso;
            });
        }

        bool PedirToken()
        {
            using (Form f = new Form())
            {
                f.Text = "Token do GitHub";
                f.FormBorderStyle = FormBorderStyle.FixedDialog;
                f.StartPosition = FormStartPosition.CenterParent;
                f.MinimizeBox = f.MaximizeBox = false;
                f.ClientSize = new Size(460, 130);
                f.Font = Font;
                Label l = new Label();
                l.Text = "Cole um token com leitura em " + Programa.Repo + ":";
                l.AutoSize = true;
                l.Location = new Point(12, 14);
                TextBox t = new TextBox();
                t.UseSystemPasswordChar = true;
                t.Location = new Point(14, 40);
                t.Size = new Size(430, 26);
                LinkLabel como = new LinkLabel();
                como.Text = "Como criar um token";
                como.AutoSize = true;
                como.Location = new Point(12, 92);
                como.LinkClicked += delegate { MostrarComoCriarToken(); };
                Button ok = new Button();
                ok.Text = "Salvar";
                ok.DialogResult = DialogResult.OK;
                ok.Location = new Point(364, 86);
                f.Controls.AddRange(new Control[] { l, t, como, ok });
                f.AcceptButton = ok;
                if (f.ShowDialog(this) != DialogResult.OK || t.Text.Trim().Length == 0) return false;
                if (!GitHub.TemAcesso(t.Text.Trim()))
                {
                    MessageBox.Show(this, "Esse token não tem acesso ao " + Programa.Repo + ".", "Token do GitHub",
                                    MessageBoxButtons.OK, MessageBoxIcon.Warning);
                    return false;
                }
                Token.Salvar(pastaBase, t.Text.Trim());
                return true;
            }
        }

        // --- o trabalho (fora da thread da tela) ---

        string VersaoInstalada()
        {
            string arq = Path.Combine(Jogo, "versao.txt");
            try { return File.Exists(arq) ? File.ReadAllText(arq).Trim() : null; } catch { return null; }
        }

        static Version ParaVersao(string texto)
        {
            try { return new Version((texto ?? "0.0.0").TrimStart('v', 'V').Trim()); } catch { return new Version(0, 0, 0); }
        }

        void Trabalhar(bool semAtualizar)
        {
            try
            {
                ApagarLauncherVelho();
                if (Process.GetProcessesByName("NexusRoyale").Length > 0)
                {
                    Erro("O jogo já está aberto. Feche-o para atualizar.", false);
                    return;
                }
                string instalada = VersaoInstalada();
                if (!semAtualizar)
                {
                    Status("Procurando atualizações…");
                    string token = Token.Pegar(pastaBase);
                    Dictionary<string, object> rel = null;
                    try { rel = GitHub.UltimaRelease(token); }
                    catch (ErroAcesso e)
                    {
                        Erro(e.Message, true);
                        return;
                    }
                    catch (Exception e)
                    {
                        if (instalada == null || !(e is ErroRede || e is ErroSemVersao)) throw;
                        Status(e.Message + " Abrindo a versão instalada…");
                        Thread.Sleep(1500);
                    }
                    if (rel != null)
                    {
                        string ultima = ((string)rel["tag_name"]).TrimStart('v', 'V');
                        Directory.CreateDirectory(Baixados);
                        string manArq = Path.Combine(Baixados, "manifest.json");
                        if (File.Exists(manArq)) File.Delete(manArq);
                        GitHub.Baixar(GitHub.Asset(rel, "manifest.json"), manArq, token, 0, delegate { }, delegate { return cancelar; });
                        Dictionary<string, object> man = GitHub.LerJson(manArq);

                        if (man.ContainsKey("launcher") && AtualizarLauncher(rel, (Dictionary<string, object>)man["launcher"], token))
                            return;
                        if (Programa.TemOpcao("forcar") || instalada == null || ParaVersao(ultima) > ParaVersao(instalada))
                            InstalarVersao(rel, man, ultima, token);
                        else
                            Status("Você já está na última versão (" + instalada + ").");
                    }
                }
                if (!File.Exists(ExeJogo))
                {
                    Erro("O jogo não está instalado, e não deu para baixar.", false);
                    return;
                }
                if (Programa.TemOpcao("soAtualizar"))
                {
                    Status("Pronto. Versão instalada: " + VersaoInstalada() + ".");
                    return;
                }
                GarantirVisualCpp();
                Status("Abrindo o Nexus Royale " + VersaoInstalada() + "…");
                Process.Start(new ProcessStartInfo(ExeJogo, Programa.ArgsDoJogo()) { WorkingDirectory = Jogo });
                Thread.Sleep(1200);
                NaTela(delegate { Close(); });
            }
            catch (Cancelado) { }
            catch (ErroAcesso e) { Erro(e.Message, true); }
            catch (Exception e) { Erro(e.Message, false); }
        }

        static string Hash(string arq, Action<long, long> progresso)
        {
            using (SHA256 sha = SHA256.Create())
            using (FileStream f = File.OpenRead(arq))
            {
                byte[] buf = new byte[1 << 20];
                long feito = 0, total = f.Length;
                int n;
                while ((n = f.Read(buf, 0, buf.Length)) > 0)
                {
                    sha.TransformBlock(buf, 0, n, null, 0);
                    feito += n;
                    progresso(feito, total);
                }
                sha.TransformFinalBlock(buf, 0, 0);
                StringBuilder sb = new StringBuilder();
                foreach (byte b in sha.Hash) sb.Append(b.ToString("x2"));
                return sb.ToString();
            }
        }

        void InstalarVersao(Dictionary<string, object> rel, Dictionary<string, object> man, string versao, string token)
        {
            object[] partes = (object[])man["partes"];
            long total = 0;
            foreach (object o in partes) total += Convert.ToInt64(((Dictionary<string, object>)o)["bytes"]);

            long precisa = total * 2 + 500L * 1048576;
            long livre = new DriveInfo(Path.GetPathRoot(pastaBase)).AvailableFreeSpace;
            if (livre < precisa)
                throw new Exception(string.Format("Falta espaço em {0}: a versão {1} precisa de {2:0.0} GB livres e há {3:0.0} GB.",
                                                  Path.GetPathRoot(pastaBase), versao, precisa / 1073741824.0, livre / 1073741824.0));

            Directory.CreateDirectory(Baixados);
            List<string> arquivos = new List<string>();
            long antes = 0;
            for (int i = 0; i < partes.Length; i++)
            {
                Dictionary<string, object> p = (Dictionary<string, object>)partes[i];
                string nome = (string)p["nome"];
                long bytes = Convert.ToInt64(p["bytes"]);
                string sha = ((string)p["sha256"]).ToLowerInvariant();
                string arq = Path.Combine(Baixados, nome);
                string rotulo = "Baixando o Nexus Royale " + versao + (partes.Length > 1 ? string.Format(" (parte {0} de {1})", i + 1, partes.Length) : "") + "…";
                if (File.Exists(arq) && new FileInfo(arq).Length > bytes) File.Delete(arq);
                if (!File.Exists(arq) || new FileInfo(arq).Length < bytes)
                {
                    long base0 = antes;
                    inicioDownload = DateTime.Now;
                    baixadoAntes = base0 + (File.Exists(arq) ? new FileInfo(arq).Length : 0);
                    GitHub.Baixar(GitHub.Asset(rel, nome), arq, token, bytes,
                                  delegate (long f, long t) { Progresso(rotulo, base0 + f, total, true); },
                                  delegate { return cancelar; });
                }
                string conferir = "Conferindo " + nome + "…";
                if (Hash(arq, delegate (long f, long t) { Progresso(conferir, f, t, false); }) != sha)
                {
                    File.Delete(arq);
                    throw new Exception("O arquivo " + nome + " chegou corrompido e foi apagado. Clique em \"Tentar de novo\".");
                }
                arquivos.Add(arq);
                antes += bytes;
            }

            string zip = Path.Combine(Baixados, (string)man["zip"]);
            if (arquivos.Count > 1)
            {
                using (FileStream saida = new FileStream(zip, FileMode.Create, FileAccess.Write))
                {
                    long feito = 0;
                    byte[] buf = new byte[1 << 20];
                    foreach (string a in arquivos)
                        using (FileStream entrada = File.OpenRead(a))
                        {
                            int n;
                            while ((n = entrada.Read(buf, 0, buf.Length)) > 0)
                            {
                                saida.Write(buf, 0, n);
                                feito += n;
                                Progresso("Juntando as partes…", feito, total, false);
                            }
                        }
                }
                foreach (string a in arquivos) File.Delete(a);
                if (Hash(zip, delegate (long f, long t) { Progresso("Conferindo o pacote…", f, t, false); }) !=
                    ((string)man["zip_sha256"]).ToLowerInvariant())
                {
                    File.Delete(zip);
                    throw new Exception("O pacote juntado não confere. Clique em \"Tentar de novo\".");
                }
            }

            string novo = Path.Combine(pastaBase, "game.novo");
            string antigo = Path.Combine(pastaBase, "game.antigo");
            if (Directory.Exists(novo)) Directory.Delete(novo, true);
            Directory.CreateDirectory(novo);
            string raizNovo = Path.GetFullPath(novo) + Path.DirectorySeparatorChar;
            long extraido = 0;
            using (ZipArchive z = ZipFile.OpenRead(zip))
            {
                long totalZip = 0;
                foreach (ZipArchiveEntry e in z.Entries) totalZip += e.Length;
                foreach (ZipArchiveEntry e in z.Entries)
                {
                    if (cancelar) throw new Cancelado();
                    string destino = Path.GetFullPath(Path.Combine(novo, e.FullName));
                    if (!destino.StartsWith(raizNovo, StringComparison.OrdinalIgnoreCase))
                        throw new Exception("O pacote tem um caminho inválido: " + e.FullName);
                    if (e.FullName.EndsWith("/")) { Directory.CreateDirectory(destino); continue; }
                    Directory.CreateDirectory(Path.GetDirectoryName(destino));
                    e.ExtractToFile(destino, true);
                    extraido += e.Length;
                    Progresso("Instalando…", extraido, totalZip, false);
                }
            }
            if (!File.Exists(Path.Combine(novo, "NexusRoyale.exe"))) throw new Exception("O pacote não tem o NexusRoyale.exe.");
            File.WriteAllText(Path.Combine(novo, "versao.txt"), versao);

            // Guarda as configurações (resolução, qualidade), se a versão anterior as gravou na pasta do jogo.
            string savedVelho = Path.Combine(Jogo, @"NexusRoyale\Saved");
            string savedNovo = Path.Combine(novo, @"NexusRoyale\Saved");
            if (Directory.Exists(savedVelho) && !Directory.Exists(savedNovo)) CopiarPasta(savedVelho, savedNovo);

            Status("Trocando a versão…");
            if (Directory.Exists(antigo)) Directory.Delete(antigo, true);
            if (Directory.Exists(Jogo)) Repetir(delegate { Directory.Move(Jogo, antigo); });
            Repetir(delegate { Directory.Move(novo, Jogo); });
            try { if (Directory.Exists(antigo)) Directory.Delete(antigo, true); } catch { }
            try { Directory.Delete(Baixados, true); } catch { }
            Instalacao.RegistrarVersao(versao, extraido);
            Status("Nexus Royale " + versao + " instalado.");
        }

        // O antivírus às vezes segura um arquivo recém-extraído por um instante.
        static void Repetir(Action a)
        {
            for (int i = 0; ; i++)
            {
                try { a(); return; }
                catch (IOException) { if (i >= 9) throw; Thread.Sleep(1000); }
                catch (UnauthorizedAccessException) { if (i >= 9) throw; Thread.Sleep(1000); }
            }
        }

        static void CopiarPasta(string de, string para)
        {
            Directory.CreateDirectory(para);
            foreach (string a in Directory.GetFiles(de)) File.Copy(a, Path.Combine(para, Path.GetFileName(a)), true);
            foreach (string d in Directory.GetDirectories(de)) CopiarPasta(d, Path.Combine(para, Path.GetFileName(d)));
        }

        // Troca o próprio .exe quando a Release traz um launcher mais novo, e abre o novo no lugar.
        bool AtualizarLauncher(Dictionary<string, object> rel, Dictionary<string, object> info, string token)
        {
            if (ParaVersao((string)info["versao"]) <= ParaVersao(Programa.Versao)) return false;
            string exe = Application.ExecutablePath;
            string novo = exe + ".novo";
            string velho = exe + ".velho";
            Status("Atualizando o launcher para a versão " + info["versao"] + "…");
            if (File.Exists(novo)) File.Delete(novo);
            GitHub.Baixar(GitHub.Asset(rel, (string)info["nome"]), novo, token, Convert.ToInt64(info["bytes"]),
                          delegate (long f, long t) { Progresso("Atualizando o launcher…", f, t, false); },
                          delegate { return cancelar; });
            if (Hash(novo, delegate { }) != ((string)info["sha256"]).ToLowerInvariant())
            {
                File.Delete(novo);
                throw new Exception("O launcher novo chegou corrompido. Clique em \"Tentar de novo\".");
            }
            if (File.Exists(velho)) File.Delete(velho);
            File.Move(exe, velho);   // o Windows deixa renomear o .exe em uso
            File.Move(novo, exe);
            Process.Start(new ProcessStartInfo(exe, string.Join(" ", Array.ConvertAll<string, string>(Programa.Args,
                delegate (string a) { return a.Contains(" ") ? "\"" + a + "\"" : a; }))) { WorkingDirectory = pastaBase });
            NaTela(delegate { Close(); });
            return true;
        }

        static void ApagarLauncherVelho()
        {
            string velho = Application.ExecutablePath + ".velho";
            for (int i = 0; i < 5 && File.Exists(velho); i++)
            {
                try { File.Delete(velho); } catch { Thread.Sleep(500); }
            }
        }

        // O jogo é compilado com o MSVC 14.50: precisa do Visual C++ 2015-2026 nessa versão ou mais nova.
        void GarantirVisualCpp()
        {
            try
            {
                using (RegistryKey k = RegistryKey.OpenBaseKey(RegistryHive.LocalMachine, RegistryView.Registry64)
                                                  .OpenSubKey(@"SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64"))
                {
                    if (k != null && Convert.ToInt32(k.GetValue("Installed", 0)) == 1 && Convert.ToInt32(k.GetValue("Minor", 0)) >= 50)
                        return;
                }
            }
            catch { }
            string prereq = Path.Combine(Jogo, @"Engine\Extras\Redist\en-us\UEPrereqSetup_x64.exe");
            if (!File.Exists(prereq)) return;
            Status("Instalando o Visual C++ da Microsoft (o Windows vai pedir permissão)…");
            try
            {
                using (Process p = Process.Start(new ProcessStartInfo(prereq, "/quiet /norestart") { UseShellExecute = true, Verb = "runas" }))
                    p.WaitForExit();
            }
            catch { }   // recusou o UAC: tenta abrir o jogo mesmo assim
        }
    }
}
