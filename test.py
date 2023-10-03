def main():
        print("Before file writing")
        data = f"User ID: 23425345, Username: @Maleda\n"
        with open("user_list.txt", "a", encoding="utf-8") as file:
                    file.write(data)
                    file.flush()
                    print 
        print("After file writing")
        
if __name__ == "__main__":
    main()
