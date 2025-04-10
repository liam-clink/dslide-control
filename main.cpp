#include "PerformaxCom.h"
#include <iostream>
#include <format>

#define PERFORMAX_RETURN_SERIAL_NUMBER 0
#define PERFORMAX_RETURN_DESCRIPTION 1

// void Connect(HANDLE *device_handle)
// {
//     CString str, strErr;
//     int n1, n2;
//     if (fnPerformaxComSetTimeouts(10000, 10000))
//     {
//         n1 = m_CombDeviceList.GetCurSel();
//         if (!fnPerformaxComOpen(n1, device_handle))
//         {
//             n2 = m_CombDeviceList.GetLBTextLen(n1);
//             m_CombDeviceList.GetLBText(n1, str.GetBuffer(n2));
//             str.ReleaseBuffer();
//             std::cout << "Error opening device. Reset hardware and try again." << std::endl;
//         }
//         else
//         {
//             std::cout << "Device is connected." << std::endl;
//         }
//     }
//     else
//         MessageBox("Error to set timeouts. Reset hardware and try again.");
// }

int main()
{
    DWORD device_count;
    if (!fnPerformaxComGetNumDevices(&device_count))
    {
        std::cout << "Error finding USB devices." << std::endl;
        return -1;
    }
    std::cout << "There are this many Performax devices connected: "
              << device_count << std::endl;

    char device_name[128];
    HANDLE device_handle = nullptr;
    for (size_t i = 0; i < device_count; i++)
    {
        fnPerformaxComSetTimeouts(1000, 1000);
        fnPerformaxComOpen(i, &device_handle);
        fnPerformaxComFlush(device_handle);
        fnPerformaxComGetProductString(i, &device_name, PERFORMAX_RETURN_SERIAL_NUMBER);
        fnPerformaxComClose(device_handle);
        std::cout << "Device name: " << device_name << std::endl;
    }

    fnPerformaxComSetTimeouts(1000, 1000);
    fnPerformaxComOpen(0, &device_handle);
    fnPerformaxComFlush(device_handle);
    std::cout << device_handle << std::endl;

    // Command and reply buffers need to be 64 bytes
    // Not sure why the length of the buffers is an arg to the command function...
    char command_buffer[64];
    char reply_buffer[64];

    // Get current position index
    // strcpy(command_buffer, "PX");
    // strcpy(command_buffer, "HSPD"); // 25000 = 10 mm/s For our D-Slide
    strcpy(command_buffer, "X-1000000"); // -1250000 = -500 mm for our D-slide

    fnPerformaxComSendRecv(device_handle, command_buffer, 64, 64, reply_buffer);
    std::cout << reply_buffer << std::endl;

    fnPerformaxComClose(device_handle);

    return 0;
}
