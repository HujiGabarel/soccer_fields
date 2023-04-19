import openpyxl

def save_to_excel(helipadList, filename):
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = "Helipads"

    # Write the helipad data to the worksheet
    worksheet.cell(row=1, column=1, value="X")
    worksheet.cell(row=1, column=2, value="Y")
    worksheet.cell(row=1, column=3, value="Size")
    for i, helipad in enumerate(helipadList):
        worksheet.cell(row=i+2, column=1, value=helipad[0][0])
        worksheet.cell(row=i+2, column=2, value=helipad[0][1])
        worksheet.cell(row=i+2, column=3, value=helipad[1])

    # Save the workbook
    workbook.save(filename=filename)



def mat2cords(satellitePicture, heliPadList, topLeftCords):
    helipadList = []  # The list of center of the helipads CORDS with size
    for i in heliPadList:
        center = MidOfHeliPad(i[0], i[1], i[2], i[3])  # insert the top left x and y cords then the bot_right cords.
        width = i[2] - i[0] + 1  # calculate the width of the submatrix
        height = i[3] - i[1] + 1  # calculate the height of the submatrix
        size = width * height  # calculate the size of the submatrix (area)

        # Calculate the real-world coordinates of the helipad center
        centerX, centerY = center
        realX = topLeftCords[0] + (centerX - 1)  # subtract 1 to convert from 1-based to 0-based indexing
        realY = topLeftCords[1] - (centerY - 1)  # subtract 1 and negate to convert from 1-based to 0-based indexing and flip y-axis
        realCenter = (realX, realY)

        helipadList.append((realCenter, size))

    return helipadList




def MidOfHeliPad(topLeftX, topLeftY, botRightX, botRightY):
    subMatX = botRightX - topLeftX  # length of helipad
    subMatY = botRightY - topLeftY  # width of helipad
    subMatMidX = subMatX / 2 + 1
    subMatMidY = subMatY / 2 + 1
    subMatMidX = int(subMatMidX)
    subMatMidY = int(subMatMidY)
    finalX = topLeftX + subMatMidX
    finalY = topLeftY + subMatMidY
    return finalX, finalY



def main():
    # Example inputs
    satellitePicture = [[1, 0, 0, 1, 1],
                        [1, 0, 0, 1, 1],
                        [1, 1, 1, 0, 1],
                        [0, 1, 1, 1, 1],
                        [0, 0, 1, 1, 1]]
    heliPadList = [(0, 1, 2, 2), (3, 3, 4, 4)]
    topLeftCords = (10, 10)

    # Call the mat2cords function
    # need to change topLeftCords to center cordinates
    helipadList = mat2cords(satellitePicture, heliPadList, topLeftCords)

    # Print the output of the mat2cords function
    print("Helipad List:")
    for helipad in helipadList:
        print(helipad)

    # Call the save_to_excel function
    save_to_excel(helipadList, "helipads.xlsx")

if __name__ == '__main__':
    main()


