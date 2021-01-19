from discord.ext.commands import Cog, command, Bot, errors, group
from discord import Embed, Color, User
from .base_economy import Inventory
import time
import random
from math import ceil


def setup(bot: Bot):
    # Make economy variable global
    global economy
    economy = bot.economy
    # Add AuctionHouse to bot's cogs
    cog = AuctionHouse(bot)
    cog.refresh_auctions_from_save()
    bot.add_cog(cog)


bid_increase = 1.05


class Auction:
    """Auction"""
    def __init__(
        self,
        cog: Cog,
        owner_id: int,
        artifact: str,
        duration: int,
        starting_bid: int,
        quantity: int = 1
    ):
        self.cog = cog
        self.name = artifact
        self.quantity = quantity
        self.end = duration + time.time()  # To tell when auction is done
        self.starting_bid = starting_bid
        self.owner = owner_id
        self.bids = []
        self.collected = False
        self.id = random.randint(  # Random id
            1_000_000_000,
            9_999_999_999
        )

        self.cog.auctions[str(self.id)] = self  # Add auction to auctions list

    @property
    def current_bid(self):  # Current top bid
        if len(self.bids) >= 1:
            return self.bids[-1]

    def has_enough_money(self, user_id, price) -> bool:
        """Check if user has enough coins"""
        coins = economy[str(user_id)]['coins']
        if coins >= price:
            economy[str(user_id)]['coins'] -= price
            economy.save()
        return coins >= price

    def return_previous_bid(self):
        try:
            bidder, bid = self.bids[-2]
            economy[str(bidder)]['coins'] += bid  # Give coins back to previous bidder
            economy.save()
        except IndexError:
            return


    def bid(self, ctx, price: int):
        if self.end < time.time():
            raise errors.UserInputError("This auction is already done.")

        if self.current_bid:  # If it is the starting bid or not

            if not price > self.current_bid[-1] * bid_increase:  # If it is large enough
                raise errors.UserInputError("You have to bid higher than the highest bid.")

            #if not ctx.author.id != self.current_bid[0]:  # If it is not the current bidder
            #    raise errors.UserInputError("You are already the highest bidder.")

            if not self.has_enough_money(ctx.author.id, price):  # If the user has enough money
                raise errors.UserInputError("You don't have enough money to bid on this artifact.")

            self.bids.append([ctx.author.id, price])
            self.return_previous_bid()

        else:
            if not price >= self.starting_bid:
                raise errors.UserInputError("You have to bid at or higher than the starting bid.")

            if not ctx.author.id != self.owner:
                raise errors.UserInputError("You are already own this.")

            if not self.has_enough_money(ctx.author.id, price):
                raise errors.UserInputError("You don't have enough money to bid on this artifact.")

            self.bids.append([ctx.author.id, price])

        self.save()


    def save(self):
        ah = self.cog.bot.auctionhouse
        ah['auctions'][str(self.id)] = {
            'bids': self.bids,
            'artifact': self.name,
            'ends_at': self.end,
            'starting_bid': self.starting_bid,
            'owner': self.owner,
            'quantity': self.quantity
        }
        ah.save()


    def delete(self):
        ah = self.cog.bot.auctionhouse
        del ah['auctions'][str(self.id)]
        del self.cog.auctions[str(self.id)]

        del self


class AuctionHouse(Cog):
    """auction"""
    def __init__(self, bot: Bot):
        self.bot = bot
        self.auctions = {}

    def refresh_auctions_from_save(self):
        ah = self.bot.auctionhouse
        auctions = ah['auctions']
        objs = []

        for a_id in auctions:
            values = auctions[str(a_id)]
            a = Auction(
                self,
                values['owner'],
                values['artifact'],
                0,
                values['starting_bid'],
                values['quantity']
            )
            a.end = values['ends_at']
            a.bids = values['bids']
            a.id = str(a_id)
            objs.append(a)

        self.auctions = dict([(str(x.id), x) for x in objs])


    async def auction_embed(self, auction: Auction):
        top_bid = auction.current_bid
        if top_bid:
            top_bid = top_bid[1]

        quantity_mark = f'{auction.quantity}x ' if auction.quantity > 1 else ''
        suffix = economy['suffixes'][auction.name] if auction.name in economy['suffixes'] else ''

        color = Color.from_rgb(147, 175, 194) if not economy[str(auction.owner)]['color'] else getattr(Color, economy[str(auction.owner)]['color'])()

        embed = Embed(
            title=f"Auction for {quantity_mark}{auction.name}{suffix}",
            description=str(auction.id),
            color=color
        )

        embed.add_field(name="Seller", value=str(await self.bot.fetch_user(auction.owner)))
        embed.add_field(name="Top bid", value=str(top_bid))
        embed.add_field(
            name="Minimum next bid",
            value=str(ceil(top_bid * bid_increase) if top_bid else auction.starting_bid)
        )
        embed.add_field(name="Total bids", value=str(len(auction.bids)))

        t = round((auction.end - time.time())/60)
        embed.add_field(name="Time remaining", value=(str(t)+" mins") if t >= 0 else "**DONE**")

        return embed


    def get_user_auctions(self, user_id):
        result = []
        for auction in self.auctions.values():
            if auction.owner == user_id:
                result.append(auction)
        return result

    @command(name='bid')
    async def bid(self, ctx, bid: int, auction_id: int = None):
        """Bid on a auction using the reply feature"""
        if str(ctx.author.id) not in economy:
            economy[str(ctx.author.id)] = economy['default_economy']

        if auction_id is None:
            if ctx.message.reference is None:
                raise errors.UserInputError('You must reply to a auction embed to use this command')

            msg = await ctx.fetch_message(ctx.message.reference.message_id)

            auction_id = msg.embeds[0].description
        auction = self.auctions[auction_id]

        auction.bid(ctx, bid)
        await ctx.send(f":white_check_mark: Successfully bidded on {auction.name}",
                       embed=await self.auction_embed(auction))

    @group(name="auction", invoke_without_command=True, aliases=["ah"])
    async def auction(
        self,
        ctx,
        artifact: str,
        starting_bid: int,
        duration: int,
        quantity: int = 1
    ):
        """auction [create/list/collect]"""
        await ctx.invoke(
            self.create_auction,
            artifact=artifact,
            starting_bid=starting_bid,
            duration=duration,
            quantity=quantity
        )

    @auction.command(name="collect")
    async def collect(self, ctx):
        """Collect user's finished auctions"""
        if str(ctx.author.id) not in economy:
            economy[str(ctx.author.id)] = economy['default_economy']

        collected = []
        total_coins = 0

        t = time.time()
        items = self.get_user_auctions(ctx.author.id)

        for auction in self.auctions.items():
            owner = auction.current_bid[0] if auction.current_bid else auction.owner
            if not auction.collected and auction.end < t and ctx.author.id == owner:
                quantity_mark = f'{auction.quantity}x ' if auction.quantity > 1 else ''
                suffix = economy["suffixes"][auction.name] if auction.name in economy['suffixes'] else ""

                inv = Inventory(economy[str(ctx.author.id)]['inventory'])
                for i in range(auction.quantity):
                    inv + auction.name
                
                economy[str(ctx.author.id)]['inventory'] = inv.contents
                auction.collected = True

                collected.append(f"Collected {quantity_mark}{auction.name}{suffix}")


        for auction in items:
            if auction.end < t:
                quantity_mark = f'{auction.quantity}x ' if auction.quantity > 1 else ''
                top_bid = auction.current_bid[-1] if auction.current_bid else "no"
                suffix = economy["suffixes"][auction.name] if auction.name in economy['suffixes'] else ""

                collected.append(f"{quantity_mark}{auction.name}{suffix} made {top_bid} coins")
                if top_bid != 'no':
                    total_coins += top_bid

                auction.delete()
        
        economy[str(ctx.author.id)]['coins'] += total_coins

        embed = Embed(title=f"{len(collected)} of your auctions have been collected.",
                      description="\n".join(collected),
                      color=Color.green())
        
        embed.add_field(name="Coins made", value=total_coins)
        embed.add_field(name="Total coins", value=economy[str(ctx.author.id)]['coins'])

        await ctx.send(embed=embed)

    @auction.command(name="list")
    async def list_auctions(self, ctx, user: User = None):
        """List user's auctions"""
        if user is None:
            user = ctx.author

        if str(user.id) not in economy:
            economy[str(user.id)] = economy['default_economy']

        auctions = self.get_user_auctions(user.id)
        for auction in auctions:
            await ctx.send(embed=await self.auction_embed(auction))
        if not auctions:
            await ctx.send(embed=Embed(title="No active auctions. Start some using `ah/auction`"))

    @auction.command(name="create")
    async def create_auction(
        self,
        ctx,
        artifact: str,
        starting_bid: int,
        duration: int,
        quantity: int = 1
    ):
        if str(ctx.author.id) not in economy:
            economy[str(ctx.author.id)] = economy['default_economy']

        if quantity < 1:
            raise errors.UserInputError(f"Quantity must be one or more")
        if [artifact, quantity] not in Inventory(economy[str(ctx.author.id)]['inventory']):
            raise errors.UserInputError(f'You do not have {quantity} of {artifact}')
        if duration < 1:
            raise errors.UserInputError("Duration must be five minutes or greater")
        if starting_bid < 5:
            raise errors.UserInputError("Starting bid must be at least 5 coins")

        duration *= 60

        auction = Auction(self, ctx.author.id, artifact, duration, starting_bid, quantity)
        auction.save()

        economy[str(ctx.author.id)]['inventory'][artifact] -= quantity

        await ctx.send(embed=await self.auction_embed(auction))

