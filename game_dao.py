from battlefield import Battlefield
from vessel import Vessel
from weapon import Weapon
import game as game
from numpy import select
from sqlalchemy import create_engine, Column, Integer, ForeignKey, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship


engine = create_engine('sqlite:///C:/Users/HP/Documents/THEONE/bataillenavalemain1/bataillenavalemain2/tmp/tdlog.db', echo=True, future=True)
Base = declarative_base(bind=engine)
Session = sessionmaker(bind=engine)

class Player:
    def __init__(self,id:int, name: str, battle_field: Battlefield):
        self.battle_field = battle_field
        self.name = name
    def get_name(self):
        return self.name
    def get_battlefield(self):
        return self.battle_field

class Game:
    def __init__(self, id=None):
        self.players =[]
    def get_players(self):
        return self.players
    def add_player(self, player:Player):
        self.players.append(player)


class GameEntity(Base):
    __tablename__ = 'game'
    id = Column(Integer, primary_key=True)
    player = relationship("PlayerEntity", back_populates="game", cascade="all, delete-orphan")


class PlayerEntity(Base):
    __tablename__ = 'player'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    game_id = Column(Integer, ForeignKey("game.id"), nullable=False)
    game = relationship("GameEntity", back_populates="player")
    battle_field_id = Column(Integer, ForeignKey("battlefield.id"))
    battle_field = relationship("BattlefieldEntity", back_populates="player", uselist=False, cascade="all, delete-orphan")


class BattlefieldEntity(Base):
    __tablename__ = 'battlefield'
    id = Column(Integer, primary_key=True)
    min_x = Column(Integer, nullable=False)
    min_y = Column(Integer, nullable=False)
    min_z = Column(Integer, nullable=False)
    max_x = Column(Integer, nullable=False)
    max_y = Column(Integer, nullable=False)
    max_z = Column(Integer, nullable=False)
    max_power = Column(Integer, nullable=False)
    player_id = Column(Integer, ForeignKey("player.id"), nullable=False)
    player = relationship("PlayerEntity", back_populates="battlefield")
    vessel = relationship("VesselEntity", back_populates="battlefield", uselist=False, cascade="all, delete-orphan")

class VesselEntity(Base):
    __tablename__ = 'vessel'
    id = Column(Integer, primary_key=True)
    coord_x = Column(Integer, nullable=False)
    coord_y = Column(Integer, nullable=False)
    coord_z = Column(Integer, nullable=False)
    hots_to_be_destroyed = Column(Integer, nullable=False)
    type = Column(String, nullable=False)
    battle_field_id = Column(Integer, ForeignKey("battlefield.id"), nullable=False)
    battlefield = relationship("BattlefieldEntity", back_populates="vessel")
    weapon = relationship("WeaponEntity",
                          back_populates="vessel",
                          uselist=False, cascade="all, delete-orphan")


class WeaponEntity(Base):
    __tablename__ = 'weapon'
    id = Column(Integer, primary_key=True)
    ammunitions = Column(Integer, nullable=False)
    range = Column(Integer, nullable=False)
    type = Column(String, nullable=False)
    player_id = Column(Integer, ForeignKey("player.id"), nullable=False)
    vessel_id = Column(Integer, ForeignKey("vessel.id"), nullable=False)
    vessel = relationship("VesselEntity", back_populates="weapon")
    player = relationship("PlayerEntity", back_populates="weapon")

Base.metadata.create_all()

class GameDao:
    def __init__(self):
        Base.metadata.create_all()
        self.db_session = Session()
    def map_to_game_entity(self,game:Game):
        game_entity = GameEntity()
        game_entity.id = game.id
        game_entity.player = game.players
        return game_entity
    def map_to_game(self, game_entity:GameEntity):
        id =game_entity.id
        game = Game(id)
        return game

    def map_to_game_entity(self,game: Game) -> GameEntity:
        game_entity = GameEntity(id=game.id)
        game_entity.players = [self.map_to_player_entity(player) for player in game.players]
        return game_entity

    def map_to_player_entity(self, player: Player) -> PlayerEntity:
        player_entity = PlayerEntity(id=player.id, name=player.name, game_id=player.game.id)
        player_entity.battle_field = self.map_to_battlefield_entity(player.battle_field, player_entity.id)
        return player_entity

    def map_to_battlefield_entity(self, battlefield: Battlefield, player_id: int) -> BattlefieldEntity:
        battlefield_entity = BattlefieldEntity(id=battlefield.id,
                                               min_x=battlefield.min_x,
                                               min_y=battlefield.min_y,
                                               min_z=battlefield.min_z,
                                               max_x=battlefield.max_x,
                                               max_y=battlefield.max_y,
                                               max_z=battlefield.max_z,
                                               max_power=battlefield.max_power,
                                               player_id=player_id)
        battlefield_entity.vessels = [self.map_to_vessel_entity(vessel, battlefield_entity.id) for vessel in
                                      battlefield.vessels]
        return battlefield_entity

    def map_to_vessel_entity(self, vessel: Vessel, battlefield_id: int) -> VesselEntity:
        vessel_entity = VesselEntity(id=vessel.id,
                                     coord_x=vessel.coord_x,
                                     coord_y=vessel.coord_y,
                                     coord_z=vessel.coord_z,
                                     hots_to_be_destroyed=vessel.hots_to_be_destroyed,
                                     type=vessel.type,
                                     battle_field_id=battlefield_id)
        vessel_entity.weapon = self.map_to_weapon_entity(vessel.weapon, vessel_entity.id)
        return vessel_entity

    def map_to_weapon_entity(self, weapon: Weapon, vessel_id: int) -> WeaponEntity:
        weapon_entity = WeaponEntity(id=weapon.id,
                                     ammunitions=weapon.ammunitions,
                                     range=weapon.range,
                                     type=weapon.type,
                                     vessel_id=vessel_id)
        return weapon_entity

    def create_game(self, game: game) :
        game_entity = self.map_to_game_entity(game)
        self.db_session.add(game_entity)
        self.db_session.commit()
        return game_entity.id
    def find_game(self, game_id: int):
        stmt = select(GameEntity).where(GameEntity.id == game_id)
        game_entity = self.db_session.scalars(stmt).one()
        return self.map_to_game(game_entity)