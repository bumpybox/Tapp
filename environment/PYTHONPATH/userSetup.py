try:
    __import__("tapp")

except ImportError as e:
    print("tapp: Could not load integration: %s " % e)

else:

    import tapp

    # Setup integration
    tapp.setup()
