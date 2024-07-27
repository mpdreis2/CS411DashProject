from neo4j import GraphDatabase
address="neo4j://localhost:7687"
auth=('neo4j', "ilovecs411")
driver = GraphDatabase.driver(address, auth=auth)
#password may be ilovecs411
if __name__ == "__main__":
    driver.verify_connectivity()
    print("working")