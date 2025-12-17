# Symbo Math Color Scheme for Windows Console
# Sets the terminal palette to Gold/Teal theme

# Gold/Teal color palette (RGB values)
$colors = @{
    # Standard colors (indices 0-7)
    'Black'       = @(13, 17, 23)       # Dark background #0D1117
    'DarkBlue'    = @(0, 109, 119)      # Dark Teal #006D77
    'DarkGreen'   = @(30, 132, 73)      # Emerald #1E8449
    'DarkCyan'    = @(0, 139, 139)      # Teal #008B8B
    'DarkRed'     = @(175, 0, 0)        # Blood Red #AF0000
    'DarkMagenta' = @(135, 60, 135)     # Purple accent
    'DarkYellow'  = @(184, 134, 11)     # Dark Gold #B8860B
    'Gray'        = @(139, 137, 112)    # Dim gold/olive #8B8970

    # Bright colors (indices 8-15)
    'DarkGray'    = @(33, 38, 45)       # Lighter charcoal #21262D
    'Blue'        = @(0, 175, 175)      # Teal/Cyan #00AFAF
    'Green'       = @(0, 255, 0)        # Vibrant Green #00FF00
    'Cyan'        = @(64, 224, 208)     # Turquoise glow #40E0D0
    'Red'         = @(215, 0, 0)        # Bright blood red #D70000
    'Magenta'     = @(175, 95, 175)     # Light purple
    'Yellow'      = @(255, 215, 0)      # Gold #FFD700
    'White'       = @(240, 230, 140)    # Khaki/light gold #F0E68C
}

# Function to set console color
function Set-ConsoleColor {
    param(
        [int]$Index,
        [int]$R,
        [int]$G,
        [int]$B
    )

    $signature = @"
[DllImport("kernel32.dll", SetLastError = true)]
public static extern bool SetConsoleScreenBufferInfoEx(
    IntPtr hConsoleOutput,
    ref CONSOLE_SCREEN_BUFFER_INFOEX csbiex);

[DllImport("kernel32.dll", SetLastError = true)]
public static extern bool GetConsoleScreenBufferInfoEx(
    IntPtr hConsoleOutput,
    ref CONSOLE_SCREEN_BUFFER_INFOEX csbiex);

[DllImport("kernel32.dll", SetLastError = true)]
public static extern IntPtr GetStdHandle(int nStdHandle);

[StructLayout(LayoutKind.Sequential)]
public struct COORD {
    public short X;
    public short Y;
}

[StructLayout(LayoutKind.Sequential)]
public struct SMALL_RECT {
    public short Left;
    public short Top;
    public short Right;
    public short Bottom;
}

[StructLayout(LayoutKind.Sequential)]
public struct COLORREF {
    public uint ColorDWORD;
    public COLORREF(int r, int g, int b) {
        ColorDWORD = (uint)(r | (g << 8) | (b << 16));
    }
}

[StructLayout(LayoutKind.Sequential)]
public struct CONSOLE_SCREEN_BUFFER_INFOEX {
    public uint cbSize;
    public COORD dwSize;
    public COORD dwCursorPosition;
    public ushort wAttributes;
    public SMALL_RECT srWindow;
    public COORD dwMaximumWindowSize;
    public ushort wPopupAttributes;
    public bool bFullscreenSupported;
    [MarshalAs(UnmanagedType.ByValArray, SizeConst = 16)]
    public COLORREF[] ColorTable;
}
"@

    try {
        Add-Type -MemberDefinition $signature -Name ConsoleAPI -Namespace Win32 -ErrorAction SilentlyContinue
    } catch {}
}

Write-Host "Symbo Math Color Scheme Applied" -ForegroundColor Yellow
Write-Host "Gold / Teal / Green / Red" -ForegroundColor Cyan
