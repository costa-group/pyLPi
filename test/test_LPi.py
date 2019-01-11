import lpi

if __name__ == "__main__":
    F, __ = lpi.tests()
    if F == 0:
        print("#" * 20)
        print("# All test passed. #")
        print("#" * 20)
